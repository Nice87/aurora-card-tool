"""Dynamic speaker grouping helper for Music Assistant in Aurora Card Tool."""
import logging
from typing import List, Optional
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraMASmartGroupHelper:
    """Manages temporary synced audio player groups across different providers."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_create_temp_group(self, master_entity_id: str, member_entity_ids: List[str]) -> bool:
        """Create a temporary synced playback group via Home Assistant / Music Assistant services."""
        try:
            await self.hass.services.async_call(
                "media_player",
                "join",
                {
                    "entity_id": master_entity_id,
                    "group_members": member_entity_ids,
                },
                blocking=True,
            )
            _LOGGER.info("Successfully created temp audio group with master %s and members %s", master_entity_id, member_entity_ids)
            return True
        except Exception as err:
            _LOGGER.error("Failed to create temporary audio group: %s", err)
            return False

    async def async_disband_temp_group(self, entity_ids: List[str]) -> bool:
        """Unjoin players from a temporary group."""
        try:
            for entity_id in entity_ids:
                await self.hass.services.async_call(
                    "media_player",
                    "unjoin",
                    {"entity_id": entity_id},
                    blocking=True,
                )
            return True
        except Exception as err:
            _LOGGER.error("Failed to disband temporary audio group: %s", err)
            return False