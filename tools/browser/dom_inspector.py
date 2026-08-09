"""DOM structural inspector and framework marker detector."""

from __future__ import annotations

import re
from typing import Dict, Any, List, Set
from urllib.parse import urljoin, urlparse
import lxml.html

from schemas.observation import WebStructureMeasurements, ArchitectureType


class DOMInspector:
    """Extracts structural measurements and framework markers from HTML/DOM."""

    FRAMEWORK_SIGNATURES = {
        ArchitectureType.WORDPRESS: [
            re.compile(r"wp-content", re.I),
            re.compile(r"wp-includes", re.I),
            re.compile(r"wp-json", re.I),
        ],
        ArchitectureType.DRUPAL: [
            re.compile(r"Drupal\.settings", re.I),
            re.compile(r"/sites/default/files", re.I),
            re.compile(r"drupal\.js", re.I),
        ],
        ArchitectureType.ANGULAR_SPA: [
            re.compile(r"ng-version", re.I),
            re.compile(r"ng-app", re.I),
            re.compile(r"_ngcontent", re.I),
        ],
        ArchitectureType.REACT_SPA: [
            re.compile(r"data-reactroot", re.I),
            re.compile(r"_reactListening", re.I),
            re.compile(r"react-dom", re.I),
        ],
        ArchitectureType.NEXTJS: [
            re.compile(r"/_next/static", re.I),
            re.compile(r"__NEXT_DATA__", re.I),
        ],
    }

    @classmethod
    def detect_frameworks(cls, html_content: str) -> List[str]:
        detected = []
        for arch_type, patterns in cls.FRAMEWORK_SIGNATURES.items():
            for pattern in patterns:
                if pattern.search(html_content):
                    detected.append(arch_type.value)
                    break
        return detected

    @classmethod
    def inspect(cls, html_content: str, base_url: str) -> WebStructureMeasurements:
        if not html_content.strip():
            return WebStructureMeasurements()

        try:
            doc = lxml.html.fromstring(html_content)
        except Exception:
            return WebStructureMeasurements()

        base_netloc = urlparse(base_url).netloc.lower()

        # 1. Total DOM Nodes and Max Depth
        all_elements = doc.xpath("//*")
        node_count = len(all_elements)

        max_depth = 0
        for el in all_elements:
            depth = len(list(el.iterancestors()))
            if depth > max_depth:
                max_depth = depth

        # 2. Links Breakdown (Internal, External, PDFs)
        links = doc.xpath("//a[@href]")
        links_count = len(links)
        internal_count = 0
        external_count = 0
        pdf_count = 0

        for a in links:
            href = (a.get("href") or "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, href)
            parsed_href = urlparse(full_url)

            if parsed_href.path.lower().endswith(".pdf"):
                pdf_count += 1

            if parsed_href.netloc.lower() == base_netloc or not parsed_href.netloc:
                internal_count += 1
            else:
                external_count += 1

        # 3. Structural Elements
        forms_count = len(doc.xpath("//form"))
        tables_count = len(doc.xpath("//table"))
        images_count = len(doc.xpath("//img"))
        script_tags_count = len(doc.xpath("//script"))
        stylesheet_tags_count = len(doc.xpath("//link[@rel='stylesheet']") + doc.xpath("//style"))

        # 4. Framework Detection
        detected_frameworks = cls.detect_frameworks(html_content)

        return WebStructureMeasurements(
            dom_node_count=node_count,
            max_dom_depth=max_depth,
            links_count=links_count,
            internal_links_count=internal_count,
            external_links_count=external_count,
            forms_count=forms_count,
            tables_count=tables_count,
            images_count=images_count,
            pdf_links_count=pdf_count,
            script_tags_count=script_tags_count,
            stylesheet_tags_count=stylesheet_tags_count,
            detected_frameworks=detected_frameworks,
        )
