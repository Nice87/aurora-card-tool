"""Matter integration helper for Aurora Card Tool."""
import logging
from typing import Any, Dict, List
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraMatterFabricHelper:
    """Manages Matter fabric inspection, commissioning status, and Thread network telemetry."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_get_matter_network_status(self) -> Dict[str, Any]:
        """Aggregate Matter nodes, fabric state, and Thread connectivity."""
        matter_nodes = []
        border_routers = []

        # Scan state machine for Matter entities
        for state in self.hass.states.async_all():
            if "matter" in state.entity_id or "thread" in state.entity_id:
                node_info = {
                    "entity_id": state.entity_id,
                    "name": state.attributes.get("friendly_name", state.entity_id),
                    "state": state.state,
                    "attributes": dict(state.attributes)
                }
                if "border_router" in state.entity_id or "thread" in state.entity_id:
                    border_routers.append(node_info)
                else:
                    matter_nodes.append(node_info)

        return {
            "total_matter_nodes": len(matter_nodes),
            "border_routers_count": len(border_routers),
            "nodes": matter_nodes,
            "border_routers": border_routers
        }