"""Constants for the Aurora Card Tool integration."""
from typing import Final

DOMAIN: Final = "aurora_card_tool"
STORAGE_VERSION: Final = 1
STORAGE_KEY: Final = f"{DOMAIN}.storage"

SIGNAL_MODULES_UPDATED: Final = "aurora_card_tool_modules_updated"
SIGNAL_PRESETS_UPDATED: Final = "aurora_card_tool_presets_updated"

ATTR_MODULES: Final = "modules"
ATTR_PRESETS: Final = "presets"
ATTR_ETAG: Final = "etag"

EVENT_AURORA_TOOL_UPDATED: Final = "aurora_card_tool.updated"