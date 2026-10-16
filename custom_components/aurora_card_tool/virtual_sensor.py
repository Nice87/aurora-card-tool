"""Virtual sensor aggregator for computing environmental indices on the backend."""
import logging
import math
from typing import Any, Dict, Optional
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class AuroraVirtualSensorAggregator:
    """Computes complex indices (Thom Discomfort Index, Vapor Pressure Deficit, Dew Point) in Python."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    def compute_dew_point(self, temp_c: float, humidity_pct: float) -> float:
        """Calculate approximate dew point temperature in Celsius."""
        a = 17.27
        b = 237.7
        alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity_pct / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        return round(dew_point, 2)

    def compute_thom_discomfort_index(self, temp_c: float, humidity_pct: float) -> float:
        """Calculate Thom Discomfort Index (DI)."""
        di = temp_c - (0.55 - (0.0055 * humidity_pct)) * (temp_c - 14.5)
        return round(di, 2)

    async def async_get_aggregated_metrics(self, temp_entity_id: str, humidity_entity_id: str) -> Dict[str, Any]:
        """Fetch states and return computed comfort metrics."""
        t_state = self.hass.states.get(temp_entity_id)
        h_state = self.hass.states.get(humidity_entity_id)

        if not t_state or not h_state:
            return {"error": "Entities not found"}

        try:
            temp = float(t_state.state)
            humidity = float(h_state.state)
            return {
                "temperature": temp,
                "humidity": humidity,
                "dew_point": self.compute_dew_point(temp, humidity),
                "discomfort_index": self.compute_thom_discomfort_index(temp, humidity)
            }
        except ValueError:
            return {"error": "Invalid state numerical values"}