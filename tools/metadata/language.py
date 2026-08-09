"""Language and multilingual support detector for Indian government portals."""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple
import lxml.html

from schemas.observation import LanguageMeasurements

# Indian Scheduled Languages Unicode Script Ranges & Identifiers
INDIAN_LANGUAGE_PATTERNS = {
    "hi": (re.compile(r"[\u0900-\u097F]"), "Hindi"),
    "bn": (re.compile(r"[\u0980-\u09FF]"), "Bengali"),
    "pa": (re.compile(r"[\u0A00-\u0A7F]"), "Punjabi"),
    "gu": (re.compile(r"[\u0A80-\u0AFF]"), "Gujarati"),
    "or": (re.compile(r"[\u0B00-\u0B7F]"), "Odia"),
    "ta": (re.compile(r"[\u0B80-\u0BFF]"), "Tamil"),
    "te": (re.compile(r"[\u0C00-\u0C7F]"), "Telugu"),
    "kn": (re.compile(r"[\u0C80-\u0CFF]"), "Kannada"),
    "ml": (re.compile(r"[\u0D00-\u0D7F]"), "Malayalam"),
    "ur": (re.compile(r"[\u0600-\u06FF]"), "Urdu"),
}

LANGUAGE_SELECTOR_KEYWORDS = [
    "select language",
    "choose language",
    "भाषा चुनें",
    "भाषा",
    "english",
    "hindi",
    "हिन्दी",
    "বাংলা",
    "தமிழ்",
    "తెలుగు",
    "मराठी",
    "ગુજરાતી",
    "ಕನ್ನಡ",
    "മലയാളം",
]


class LanguageDetector:
    """Detects primary language, regional languages, and multilingual switchers."""

    @classmethod
    def detect(cls, html_content: str) -> LanguageMeasurements:
        if not html_content.strip():
            return LanguageMeasurements()

        try:
            doc = lxml.html.fromstring(html_content)
        except Exception:
            return LanguageMeasurements()

        # 1. Check HTML lang attribute
        html_tags = doc.xpath("//html[@lang]")
        html_lang = html_tags[0].get("lang").lower().split("-")[0] if html_tags else ""

        # 2. Extract visible text
        text = doc.text_content()

        # 3. Detect Indian Scripts
        detected_indian = []
        for code, (pattern, name) in INDIAN_LANGUAGE_PATTERNS.items():
            matches = pattern.findall(text)
            if len(matches) > 10:  # Threshold of matching characters
                detected_indian.append(name)

        # 4. Detect Language Switcher Widget
        has_selector = False
        text_lower = text.lower()
        for kw in LANGUAGE_SELECTOR_KEYWORDS:
            if kw.lower() in text_lower:
                has_selector = True
                break

        # Check for select/options with language codes
        lang_selects = doc.xpath("//select[contains(@id, 'lang') or contains(@name, 'lang') or contains(@class, 'lang')]")
        if lang_selects:
            has_selector = True

        primary_lang = html_lang if html_lang in ["hi", "bn", "ta", "te", "en"] else ("hi" if "Hindi" in detected_indian else "en")
        is_multilingual = len(detected_indian) > 0 or has_selector

        return LanguageMeasurements(
            detected_primary_language=primary_lang or "en",
            detected_secondary_languages=detected_indian,
            has_language_selector=has_selector,
            is_multilingual=is_multilingual,
            supported_indian_languages=detected_indian,
        )
