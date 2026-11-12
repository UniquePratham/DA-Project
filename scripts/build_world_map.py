"""Build the world map geometry for the Future view.

Source: Natural Earth 110m country boundaries, distributed as TopoJSON by the
`world-atlas` package (public domain). The topology is decoded to plain SVG
paths here so the dashboard needs no mapping library and no network call.

Each country is keyed by its ISO-3166 numeric id, which the TopoJSON carries in
the ``id`` field. The dashboard joins that to the ISO alpha-2 codes from
pycountry, so a country's colour is driven by its real probe status rather than
by a hand-maintained list.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pycountry

TOPO = REPO / "data" / "fixtures" / "world-110m.json"
OUT = REPO / "dashboard" / "static" / "world_map.js"

WIDTH = 1000
HEIGHT = 500


def decode_arcs(topology: dict) -> list[list[tuple[float, float]]]:
    """Undo TopoJSON's delta encoding."""
    transform = topology.get("transform")
    sx, sy = transform["scale"]
    tx, ty = transform["translate"]

    arcs = []
    for arc in topology["arcs"]:
        x = y = 0
        points = []
        for dx, dy in arc:
            x += dx
            y += dy
            points.append((x * sx + tx, y * sy + ty))
        arcs.append(points)
    return arcs


def ring_points(arc_indices: list[int], arcs: list[list[tuple[float, float]]]):
    """Stitch an arc index list into a coordinate ring."""
    points: list[tuple[float, float]] = []
    for idx in arc_indices:
        if idx >= 0:
            seg = arcs[idx]
        else:
            seg = list(reversed(arcs[~idx]))
        if points and seg:
            points.extend(seg[1:])
        else:
            points.extend(seg)
    return points


def project(lon: float, lat: float) -> tuple[float, float]:
    """Equirectangular projection into the SVG viewBox."""
    x = (lon + 180.0) / 360.0 * WIDTH
    y = (90.0 - lat) / 180.0 * HEIGHT
    return x, y


def ring_to_path(points: list[tuple[float, float]]) -> str:
    if len(points) < 3:
        return ""
    parts = []
    for i, (lon, lat) in enumerate(points):
        x, y = project(lon, lat)
        parts.append(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}")
    parts.append("Z")
    return "".join(parts)


def numeric_to_alpha2() -> dict[str, str]:
    """Map ISO-3166 numeric codes to alpha-2, via pycountry."""
    out = {}
    for c in pycountry.countries:
        num = getattr(c, "numeric", None)
        if num:
            out[str(int(num))] = c.alpha_2
    return out


def main() -> int:
    topology = json.loads(TOPO.read_text(encoding="utf-8"))
    arcs = decode_arcs(topology)
    num2a2 = numeric_to_alpha2()

    countries = []
    for geom in topology["objects"]["countries"]["geometries"]:
        raw_id = geom.get("id")
        if raw_id is None:
            continue
        code = num2a2.get(str(int(raw_id)))
        if not code:
            continue

        gtype = geom["type"]
        if gtype == "Polygon":
            polygons = [geom["arcs"]]
        elif gtype == "MultiPolygon":
            polygons = geom["arcs"]
        else:
            continue

        d_parts = []
        for poly in polygons:
            for ring in poly:
                pts = ring_points(ring, arcs)
                d = ring_to_path(pts)
                if d:
                    d_parts.append(d)

        if not d_parts:
            continue

        countries.append(
            {
                "code": code,
                "name": geom.get("properties", {}).get("name", code),
                "d": "".join(d_parts),
            }
        )

    countries.sort(key=lambda c: c["code"])

    payload = {
        "width": WIDTH,
        "height": HEIGHT,
        "projection": "equirectangular",
        "source": "Natural Earth 110m via world-atlas (public domain)",
        "countries": countries,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "window.WORLD_MAP=" + json.dumps(payload, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(f"  countries with geometry: {len(countries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
