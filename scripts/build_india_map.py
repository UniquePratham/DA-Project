"""Compile a compact, offline India state map bundle for the dashboard.

The dashboard must render real geography (not a hand-drawn polygon) while still
working from a ``file://`` URL with no network access.

The upstream source is district-level. Simplifying each district ring
independently leaves hairline seams between neighbours, because a shared edge is
simplified differently on each side. So the pipeline is:

    1. project every district ring at full precision
    2. dissolve shared edges to recover the state boundary
    3. chain the surviving edges into closed rings
    4. simplify those rings once, as a single outline

That yields one clean closed polygon per state — correct fill, correct border,
no internal seams — and a much smaller bundle.

Usage:
    python scripts/build_india_map.py                  # downloads the source once
    python scripts/build_india_map.py --source path.geojson

Source: https://github.com/udit-001/india-maps-data (Census of India boundaries).
"""

from __future__ import annotations

import argparse
import json
import math
import urllib.request
from pathlib import Path

SOURCE_URL = (
    "https://raw.githubusercontent.com/udit-001/india-maps-data/main/geojson/india.geojson"
)
CACHE = Path("data/fixtures/india_states.geojson")

# Equirectangular projection scaled by the cosine of India's mean latitude keeps
# the subcontinent's proportions close enough for a choropleth at this size.
MEAN_LAT = 22.0
LON_SCALE = math.cos(math.radians(MEAN_LAT))

VIEW_W = 620.0
VIEW_H = 700.0
PADDING = 8.0

# Vertices are snapped to this many decimals before edge matching, so that
# coordinates differing only by float noise still cancel as a shared edge.
SNAP = 4


def project(lon: float, lat: float) -> tuple[float, float]:
    return lon * LON_SCALE, -lat


def perpendicular_distance(point, start, end) -> float:
    (px, py), (ax, ay), (bx, by) = point, start, end
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def simplify(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Ramer-Douglas-Peucker, iterative to avoid recursion limits on long rings."""
    if len(points) < 3:
        return points

    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]

    while stack:
        start, end = stack.pop()
        worst, worst_index = 0.0, -1
        for i in range(start + 1, end):
            dist = perpendicular_distance(points[i], points[start], points[end])
            if dist > worst:
                worst, worst_index = dist, i
        if worst > tolerance and worst_index != -1:
            keep[worst_index] = True
            stack.append((start, worst_index))
            stack.append((worst_index, end))

    return [p for p, k in zip(points, keep) if k]


def iter_rings(geometry: dict):
    if geometry["type"] == "Polygon":
        yield from geometry["coordinates"]
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield from polygon


def snap(point: tuple[float, float]) -> tuple[float, float]:
    return round(point[0], SNAP), round(point[1], SNAP)


def dissolve(rings: list[list[tuple[float, float]]]) -> list[tuple]:
    """Return boundary edges by cancelling edges shared between districts."""
    counts: dict[tuple, int] = {}
    for ring in rings:
        snapped = [snap(p) for p in ring]
        for i in range(len(snapped) - 1):
            a, b = snapped[i], snapped[i + 1]
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            counts[key] = counts.get(key, 0) + 1
    return [edge for edge, n in counts.items() if n == 1]


def chain_rings(edges: list[tuple]) -> list[list[tuple[float, float]]]:
    """Chain boundary edges into closed rings."""
    adjacency: dict[tuple, list[tuple]] = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)

    used: set[tuple] = set()
    rings: list[list[tuple[float, float]]] = []

    for start in adjacency:
        for first in adjacency[start]:
            edge = (start, first) if start < first else (first, start)
            if edge in used:
                continue

            ring = [start, first]
            used.add(edge)
            current, previous = first, start

            while True:
                candidates = [n for n in adjacency[current] if n != previous]
                if not candidates:
                    break
                nxt = candidates[0]
                edge = (current, nxt) if current < nxt else (nxt, current)
                if edge in used:
                    break
                used.add(edge)
                ring.append(nxt)
                previous, current = current, nxt
                if nxt == start:
                    break

            if len(ring) >= 4:
                rings.append(ring)

    return rings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=None, help="local GeoJSON; downloaded if omitted")
    parser.add_argument("--out", default="dashboard/static/india_map.js")
    parser.add_argument("--tolerance", type=float, default=0.03)
    args = parser.parse_args()

    if args.source:
        source_path = Path(args.source)
    elif CACHE.exists():
        source_path = CACHE
    else:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {SOURCE_URL} -> {CACHE}")
        urllib.request.urlretrieve(SOURCE_URL, CACHE)
        source_path = CACHE

    source = json.loads(source_path.read_text(encoding="utf-8"))

    # The upstream file carries both district polygons and one state-level
    # polygon per state (``district: null``). Prefer the state polygon: it is
    # already dissolved, so it fills and strokes cleanly with no internal seams.
    # Two small UTs ship only district polygons, so those fall back to a dissolve.
    state_rings: dict[str, list[list[tuple[float, float]]]] = {}
    district_rings: dict[str, list[list[tuple[float, float]]]] = {}

    for feature in source["features"]:
        state = feature["properties"].get("st_nm")
        if not state:
            continue
        is_state_polygon = feature["properties"].get("district") is None
        bucket = state_rings if is_state_polygon else district_rings

        for ring in iter_rings(feature["geometry"]):
            projected = [project(lon, lat) for lon, lat in ring]
            if len(projected) >= 3:
                bucket.setdefault(state, []).append(projected)

    outlines: dict[str, list[list[tuple[float, float]]]] = {}
    for state in set(state_rings) | set(district_rings):
        if state in state_rings:
            outlines[state] = state_rings[state]
        else:
            # Some UTs ship the same polygon twice; dedupe before dissolving or
            # every edge cancels against its own duplicate.
            unique: dict[tuple, list[tuple[float, float]]] = {}
            for ring in district_rings[state]:
                unique.setdefault(tuple(snap(p) for p in ring), ring)
            outlines[state] = chain_rings(dissolve(list(unique.values())))

    # Simplify each state outline once, and compute the global bounding box.
    min_x = min_y = math.inf
    max_x = max_y = -math.inf
    simplified: dict[str, list[list[tuple[float, float]]]] = {}

    for state, rings in outlines.items():
        kept = []
        for ring in rings:
            reduced = simplify(ring, args.tolerance)
            # A tiny island can collapse below a triangle; keep its original ring
            # rather than dropping the state from the map entirely.
            if len(reduced) < 3:
                reduced = ring
            if len(reduced) < 3:
                continue
            for x, y in reduced:
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
            kept.append(reduced)
        if kept:
            simplified[state] = kept

    span_x = max_x - min_x
    span_y = max_y - min_y
    scale = min((VIEW_W - 2 * PADDING) / span_x, (VIEW_H - 2 * PADDING) / span_y)
    offset_x = (VIEW_W - span_x * scale) / 2 - min_x * scale
    offset_y = (VIEW_H - span_y * scale) / 2 - min_y * scale

    def to_path(rings: list[list[tuple[float, float]]]) -> str:
        parts = []
        for ring in rings:
            coords = [
                f"{x * scale + offset_x:.1f} {y * scale + offset_y:.1f}" for x, y in ring
            ]
            parts.append("M" + "L".join(coords) + "Z")
        return "".join(parts)

    states = [
        {"name": name, "d": to_path(rings)} for name, rings in sorted(simplified.items())
    ]

    payload = {"width": round(VIEW_W), "height": round(VIEW_H), "states": states}

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    out_path.write_text(
        "/* Generated by scripts/build_india_map.py — do not edit by hand. */\n"
        f"window.INDIA_MAP = {body};\n",
        encoding="utf-8",
    )

    points = sum(s["d"].count("L") for s in states)
    print(
        f"Wrote {out_path} — {len(states)} states, {points:,} points, "
        f"{out_path.stat().st_size / 1024:.0f} KB"
    )


if __name__ == "__main__":
    main()
