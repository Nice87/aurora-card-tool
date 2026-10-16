"""Compatibility and validation transpiler for Aurora Card modules."""
import logging

_LOGGER = logging.getLogger(__name__)

def transpile_aurora_module(module_data: dict) -> dict:
    """Validate and normalize module data structure for Aurora Card."""
    if not isinstance(module_data, dict):
        return {}
        
    code = module_data.get("code", "")
    if isinstance(code, str) and code:
        module_data["code"] = code
        
    module_data.setdefault("version", 1)
    return module_data