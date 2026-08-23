"""DOM structural inspector, GIGW accessibility feature auditor, and framework marker detector."""

from __future__ import annotations

import re
from typing import Dict, Any, List, Set
from urllib.parse import urljoin, urlparse
import lxml.html

from schemas.observation import WebStructureMeasurements, ArchitectureType


class DOMInspector:
    """Extracts structural measurements, GIGW accessibility features, and framework markers from HTML/DOM."""

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

        has_grievance = False
        has_payment = False
        has_mobile = False
        has_social = False
        has_skip_content = False
        has_screen_reader = False

        for a in links:
            href = (a.get("href") or "").strip()
            text = (a.text_content() or "").strip().lower()
            if not href or href.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, href)
            parsed_href = urlparse(full_url)
            lower_href = href.lower()

            if parsed_href.path.lower().endswith(".pdf"):
                pdf_count += 1

            if parsed_href.netloc.lower() == base_netloc or not parsed_href.netloc:
                internal_count += 1
            else:
                external_count += 1

            # Feature detection from links
            if any(k in lower_href or k in text for k in ["cpgrams", "jansunwai", "grievance", "samadhan"]):
                has_grievance = True

            if any(k in lower_href or k in text for k in ["sbiepay", "razorpay", "echallan", "treasury", "paytm", "billdesk", "payment"]):
                has_payment = True

            if any(k in lower_href for k in ["play.google.com", "apps.apple.com"]) or "umang" in lower_href:
                has_mobile = True

            if any(k in lower_href for k in ["twitter.com", "x.com", "facebook.com", "youtube.com", "instagram.com"]):
                has_social = True

            if "skip to main content" in text or "skip to content" in text or href in ["#main-content", "#content", "#main"]:
                has_skip_content = True

            if "screen reader" in text or "accessibility statement" in text:
                has_screen_reader = True

        # 3. Structural & Form Elements
        forms_count = len(doc.xpath("//form"))
        tables_count = len(doc.xpath("//table"))
        images_count = len(doc.xpath("//img"))
        script_tags_count = len(doc.xpath("//script"))
        stylesheet_tags_count = len(doc.xpath("//link[@rel='stylesheet']") + doc.xpath("//style"))

        # Search Bar Detection
        has_search = len(doc.xpath("//input[@type='search']") + doc.xpath("//input[contains(@name, 'search') or contains(@id, 'search') or contains(@placeholder, 'search') or contains(@placeholder, 'खोज')]")) > 0

        # GIGW Font Resize & Contrast Controls
        has_font_resize = len(doc.xpath("//*[contains(@class, 'font') or contains(@id, 'font') or contains(@class, 'text-size') or contains(text(), 'A+') or contains(text(), 'A-')]")) > 0
        has_contrast = len(doc.xpath("//*[contains(@class, 'contrast') or contains(@id, 'contrast') or contains(@class, 'theme') or contains(@title, 'Contrast')]")) > 0

        # ARIA Landmarks Count
        landmarks = (
            doc.xpath("//main | //nav | //header | //footer | //aside") +
            doc.xpath("//*[@role='banner' or @role='main' or @role='navigation' or @role='contentinfo']")
        )
        aria_landmarks_count = len(landmarks)

        # GIGW Accessibility Score (0 - 100)
        gigw_score = 0.0
        if has_skip_content: gigw_score += 25.0
        if has_font_resize: gigw_score += 25.0
        if has_contrast: gigw_score += 25.0
        if has_screen_reader or aria_landmarks_count > 0: gigw_score += 25.0

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
            has_font_resize_buttons=has_font_resize,
            has_contrast_toggle=has_contrast,
            has_skip_to_content=has_skip_content,
            has_screen_reader_access=has_screen_reader,
            gigw_accessibility_score=gigw_score,
            has_search_bar=has_search,
            has_grievance_portal=has_grievance,
            has_payment_gateway=has_payment,
            has_mobile_app_links=has_mobile,
            has_social_media_links=has_social,
            aria_landmarks_count=aria_landmarks_count,
        )
