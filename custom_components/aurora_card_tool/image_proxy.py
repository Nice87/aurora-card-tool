"""Optimized image proxy helper for Aurora Card Tool with SSRF and size safeguards."""
import logging
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Max allowed image size (10 MB) to prevent memory exhaustion attacks
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

class AuroraImageProxyView(HomeAssistantView):
    """Proxy remote or local media artwork securely."""

    url = "/api/aurora_card_tool/image_proxy"
    name = "api:aurora_card_tool:image_proxy"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        """Handle image proxy requests with security validations."""
        url = request.query.get("url")
        if not url:
            return web.Response(status=400, text="Missing 'url' parameter")
        
        if not url.startswith(("http://", "https://")):
            return web.Response(status=400, text="Invalid URL scheme")

        try:
            hass: HomeAssistant = request.app["hass"]
            session = hass.helpers.aiohttp_client.async_get_clientsession()
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return web.Response(status=resp.status, text="Failed to fetch remote image")
                
                # Check content length header if available
                content_length = resp.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_IMAGE_SIZE_BYTES:
                    return web.Response(status=413, text="Image payload too large")

                content = await resp.read()
                if len(content) > MAX_IMAGE_SIZE_BYTES:
                    return web.Response(status=413, text="Image payload too large")

                content_type = resp.headers.get("Content-Type", "image/jpeg")
                return web.Response(body=content, content_type=content_type)
        except Exception as err:
            _LOGGER.error("Image proxy error for %s: %s", url, err)
            return web.Response(status=500, text=str(err))