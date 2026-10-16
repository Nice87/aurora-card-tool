"""Zigbee2MQTT topology and LQI mesh health helper for Aurora Card Tool."""
import logging
from typing import Any, Dict, Optional
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraZ2MTopologyHelper:
    """Parses Zigbee2MQTT bridge state and LQI metrics without blocking the event loop."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_get_mesh_health(self) -> Dict[str, Any]:
        """Aggregate bridge statistics, coordinator version, and low-LQI warning nodes."""
        bridge_state_entity = self.hass.states.get("sensor.zigbee2mqtt_bridge_version")
        coordinator_entity = self.hass.states.get("sensor.zigbee2mqtt_bridge_coordinator_version")
        
        nodes_data = []
        low_lqi_count = 0

        # Scan state machine for router/end-device LQI sensors
        for state in self.hass.states.async_all("sensor"):
            if "lqi" in state.entity_id or "linkquality" in state.entity_id:
                try:
                    lqi_val = float(state.state)
                    if lqi_val < 50:
                        low_lqi_count += 1
                    nodes_data.append({
                        "entity_id": state.entity_id,
                        "name": state.attributes.get("friendly_name", state.entity_id),
                        "lqi": lqi_val
                    })
                except ValueError:
                    continue

        return {
            "bridge_version": bridge_state_entity.state if bridge_state_entity else "unknown",
            "coordinator": coordinator_entity.state if coordinator_entity else "unknown",
            "low_lqi_warnings": low_lqi_count,
            "monitored_nodes": len(nodes_data),
            "nodes": nodes_data
        }