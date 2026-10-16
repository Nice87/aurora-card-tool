"""Music Assistant client connection and state router helper."""
import logging
from typing import Any, Dict, Optional
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraMAClient:
    """Manages connection states and entity discovery for Music Assistant."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_get_player_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetch normalized state for a Music Assistant player entity."""
        state = self.hass.states.get(entity_id)
        if not state:
            return None
        return {
            "entity_id": entity_id,
            "state": state.state,
            "attributes": dict(state.attributes),
            "media_title": state.attributes.get("media_title"),
            "media_artist": state.attributes.get("media_artist"),
            "media_image_url": state.attributes.get("entity_picture"),
        }