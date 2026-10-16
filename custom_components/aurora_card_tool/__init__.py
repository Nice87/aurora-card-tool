"""The Aurora Card Tool integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .storage import AuroraStorageManager
from .websocket_api import async_setup_websocket_api
from .image_proxy import AuroraImageProxyView
from .translate import AuroraTranslationHelper
from .ma_client import AuroraMAClient
from .ma_queue import AuroraMAQueueHelper
from .ma_favorites import AuroraMAFavoritesHelper
from .ma_recommendations import AuroraMARecommendationsHelper
from .ma_smart_group import AuroraMASmartGroupHelper
from .z2m_topology import AuroraZ2MTopologyHelper
from .virtual_sensor import AuroraVirtualSensorAggregator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aurora Card Tool from a config entry honoring user options."""
    # Combine data and options (options take precedence when configured)
    settings = {**entry.data, **entry.options}

    storage = AuroraStorageManager(hass)
    await storage.async_initialize()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["storage"] = storage
    hass.data[DOMAIN]["translator"] = AuroraTranslationHelper(hass)
    hass.data[DOMAIN]["virtual_sensor"] = AuroraVirtualSensorAggregator(hass)

    # Conditionally load Music Assistant helpers based on settings
    if settings.get("enable_ma_helpers", True):
        hass.data[DOMAIN]["ma_client"] = AuroraMAClient(hass)
        hass.data[DOMAIN]["ma_queue"] = AuroraMAQueueHelper(hass)
        hass.data[DOMAIN]["ma_favorites"] = AuroraMAFavoritesHelper(hass)
        hass.data[DOMAIN]["ma_recommendations"] = AuroraMARecommendationsHelper(hass)
        hass.data[DOMAIN]["ma_smart_group"] = AuroraMASmartGroupHelper(hass)

    # Conditionally load Zigbee2MQTT helpers based on settings
    if settings.get("enable_z2m_topology", True):
        hass.data[DOMAIN]["z2m_topology"] = AuroraZ2MTopologyHelper(hass)

    await async_setup_websocket_api(hass, storage)
    
    # Register image proxy view only if not already registered
    try:
        hass.http.register_view(AuroraImageProxyView())
    except Exception:
        pass

    _LOGGER.info("Aurora Card Tool initialized with options: %s", settings)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)
    return True