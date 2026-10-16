"""High-performance 3-Tier storage engine with L1 RAM cache, L2 .storage fast-boot, and L3 atomic YAML sync."""
import asyncio
import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from yaml.scanner import ScannerError
from yaml.parser import ParserError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .transpiler import transpile_aurora_module

_LOGGER = logging.getLogger(__name__)

SAFE_MODULE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+$")

class AuroraStorageManager:
    """Manages modules and presets with RAM caching and atomic disk persistence."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._modules: Dict[str, Dict[str, Any]] = {}
        self._presets: Dict[str, Dict[str, Any]] = {}
        self._etag: str = ""
        self._lock = asyncio.Lock()
        
        self._config_dir = Path(hass.config.path("aurora_card"))
        self._modules_dir = self._config_dir / "modules"
        self._presets_dir = self._config_dir / "presets"

    async def async_initialize(self) -> None:
        """Initialize storage directories and load data via L2 snapshot and L3 YAML sync."""
        def _setup_dirs() -> None:
            self._modules_dir.mkdir(parents=True, exist_ok=True)
            self._presets_dir.mkdir(parents=True, exist_ok=True)

        await self.hass.async_add_executor_job(_setup_dirs)

        stored_data = await self._store.async_load()
        if stored_data and isinstance(stored_data, dict):
            self._modules = stored_data.get("modules", {})
            self._presets = stored_data.get("presets", {})

        await self.hass.async_add_executor_job(self._sync_disk_to_ram)
        self._update_etag()

    def _sync_disk_to_ram(self) -> None:
        """Scan /config/aurora_card/modules/*.yaml and import changes safely with parser guards."""
        try:
            if not self._modules_dir.exists():
                return

            disk_files = list(self._modules_dir.glob("*.yaml")) + list(self._modules_dir.glob("*.yml"))
            for file_path in disk_files:
                module_id = file_path.stem
                if not SAFE_MODULE_ID_REGEX.match(module_id):
                    _LOGGER.warning("Skipping file with unsafe module ID format: %s", file_path.name)
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        self._modules[module_id] = transpile_aurora_module(content)
                except (ScannerError, ParserError) as parse_err:
                    _LOGGER.error("YAML syntax error in module file %s: %s", file_path, parse_err)
                except Exception as err:
                    _LOGGER.error("Failed to parse module YAML %s: %s", file_path, err)
        except Exception as err:
            _LOGGER.error("Error syncing disk modules to RAM: %s", err)

    def _update_etag(self) -> None:
        """Compute SHA-256 ETag for client caching."""
        hasher = hashlib.sha256()
        canonical_str = json.dumps({"modules": self._modules, "presets": self._presets}, sort_keys=True)
        hasher.update(canonical_str.encode("utf-8"))
        self._etag = hasher.hexdigest()[:16]

    @property
    def etag(self) -> str:
        return self._etag

    async def async_get_payload(self) -> Dict[str, Any]:
        """Return L1 RAM payload."""
        return {
            "modules": self._modules,
            "presets": self._presets,
            "etag": self._etag
        }

    async def async_save_module(self, module_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atomically save a module with strict path sanitization."""
        if not SAFE_MODULE_ID_REGEX.match(module_id):
            raise ValueError(f"Invalid module_id '{module_id}': must contain only alphanumeric characters, hyphens, and underscores.")

        async with self._lock:
            normalized = transpile_aurora_module(data)
            self._modules[module_id] = normalized
            self._update_etag()

            await self._store.async_save({
                "modules": self._modules,
                "presets": self._presets
            })

            def _write_yaml() -> None:
                self._modules_dir.mkdir(parents=True, exist_ok=True)
                file_path = self._modules_dir / f"{module_id}.yaml"
                temp_path = file_path.with_suffix(".tmp")
                with open(temp_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(normalized, f, sort_keys=False, allow_unicode=True)
                os.replace(temp_path, file_path)

            await self.hass.async_add_executor_job(_write_yaml)
            return {"module_id": module_id, "module": normalized, "etag": self._etag}

    async def async_delete_module(self, module_id: str) -> bool:
        """Delete module securely."""
        if not SAFE_MODULE_ID_REGEX.match(module_id):
            return False

        async with self._lock:
            if module_id not in self._modules:
                return False

            del self._modules[module_id]
            self._update_etag()

            await self._store.async_save({
                "modules": self._modules,
                "presets": self._presets
            })

            def _delete_file() -> None:
                file_path = self._modules_dir / f"{module_id}.yaml"
                if file_path.exists():
                    file_path.unlink()

            await self.hass.async_add_executor_job(_delete_file)
            return True