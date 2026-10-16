"""High-performance WebSocket API endpoints for Aurora Card Tool."""
import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN, EVENT_AURORA_TOOL_UPDATED
from .storage import AuroraStorageManager

async def async_setup_websocket_api(hass: HomeAssistant, storage: AuroraStorageManager) -> None:
    """Register all WebSocket command handlers."""
    websocket_api.async_register_command(hass, websocket_list_modules)
    websocket_api.async_register_command(hass, websocket_save_module)
    websocket_api.async_register_command(hass, websocket_delete_module)


@websocket_api.websocket_command({
    vol.Required("type"): "aurora_card_tool/list_modules",
    vol.Optional("etag"): str,
})
@websocket_api.async_response
async def websocket_list_modules(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Handle list modules request with ETag caching short-circuit."""
    storage: AuroraStorageManager = hass.data[DOMAIN]["storage"]
    client_etag = msg.get("etag")
    payload = await storage.async_get_payload()

    if client_etag and client_etag == payload["etag"]:
        connection.send_result(msg["id"], {"modified": False, "etag": payload["etag"]})
        return

    connection.send_result(msg["id"], {"modified": True, **payload})


@websocket_api.websocket_command({
    vol.Required("type"): "aurora_card_tool/save_module",
    vol.Required("module_id"): str,
    vol.Required("module"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_save_module(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Handle save module request with validation and atomic write."""
    storage: AuroraStorageManager = hass.data[DOMAIN]["storage"]
    module_id = msg["module_id"]
    module_data = msg["module"]

    try:
        result = await storage.async_save_module(module_id, module_data)
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_format", str(err))
        return
    except Exception as err:
        connection.send_error(msg["id"], "save_failed", f"Failed to save module: {err}")
        return

    hass.bus.async_fire(EVENT_AURORA_TOOL_UPDATED, {
        "action": "upsert",
        "module_id": module_id,
        "etag": result["etag"]
    })

    connection.send_result(msg["id"], result)


@websocket_api.websocket_command({
    vol.Required("type"): "aurora_card_tool/delete_module",
    vol.Required("module_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_delete_module(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Handle delete module request securely."""
    storage: AuroraStorageManager = hass.data[DOMAIN]["storage"]
    module_id = msg["module_id"]

    success = await storage.async_delete_module(module_id)
    if not success:
        connection.send_error(msg["id"], "not_found", f"Module {module_id} not found or invalid ID")
        return

    hass.bus.async_fire(EVENT_AURORA_TOOL_UPDATED, {
        "action": "delete",
        "module_id": module_id,
        "etag": storage.etag
    })

    connection.send_result(msg["id"], {"success": True, "etag": storage.etag})