"""Consolidated Music Assistant client, favorites, queue, and recommendation helpers."""
import logging
from typing import Any, Dict, List
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraMediaHelper:
    """Provides backend data aggregation for Music Assistant and media browsers."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_get_queue(self, player_entity_id: str) -> Dict[str, Any]:
        """Fetch active queue data for media players."""
        state = self.hass.states.get(player_entity_id)
        if not state:
            return {"items": [], "active": False}
        
        return {
            "entity_id": player_entity_id,
            "state": state.state,
            "attributes": dict(state.attributes),
            "active": state.state not in ("off", "idle", "unavailable")
        }

    async def async_get_recommendations(self) -> List[Dict[str, Any]]:
        """Fetch saved favorites or media recommendations."""
        return []