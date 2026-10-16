"""Music Assistant active playback queue management helper."""
import logging
from typing import Any, Dict, List
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraMAQueueHelper:
    """Manages active playback queues for Music Assistant entities."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_get_queue_items(self, entity_id: str) -> List[Dict[str, Any]]:
        """Retrieve current queue items or fallback to player attributes."""
        state = self.hass.states.get(entity_id)
        if not state:
            return []
        
        queue_list = state.attributes.get("queue_items", [])
        if isinstance(queue_list, list):
            return queue_list
            
        return []