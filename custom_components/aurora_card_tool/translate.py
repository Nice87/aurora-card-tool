"""Translation helper module loading JSON translation files for Aurora."""
import json
import logging
from pathlib import Path
from typing import Any, Dict
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraTranslationHelper:
    """Manages localized labels for Aurora cards and tools using standard JSON translation files."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load JSON translation files from the translations directory."""
        translations_dir = Path(__file__).parent / "translations"
        if not translations_dir.exists():
            return

        for file_path in translations_dir.glob("*.json"):
            lang_code = file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self._translations[lang_code] = json.load(f)
            except Exception as err:
                _LOGGER.error("Failed to load translation file %s: %s", file_path, err)

    def get_translation(self, language: str, key_path: str, **kwargs: Any) -> str:
        """Retrieve a translated string by dot-notation key (e.g. 'ui.saved') with formatting support."""
        lang_data = self._translations.get(language, self._translations.get("en", {}))
        
        val: Any = lang_data
        for part in key_path.split("."):
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                val = self._translations.get("en", {})
                for p in key_path.split("."):
                    if isinstance(val, dict) and p in val:
                        val = val[p]
                    else:
                        return key_path
                break

        if isinstance(val, str):
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return key_path