import os
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from collections.abc import Mapping
import logging

def deep_merge(d1: dict, d2: dict) -> dict:
    """
    Recursively merge two dictionaries, giving priority to d2.
    """
    merged = d1.copy()
    for key, value in d2.items():
        if isinstance(value, Mapping) and key in merged and isinstance(merged[key], Mapping):
            merged[key] = deep_merge(dict(merged[key]), dict(value))
        else:
            merged[key] = value
    return merged


@dataclass
class DependencyConfig:
    """Configuration for all dependency types."""
    enabled: bool
    url: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = {}


@dataclass
class Config:
    """Default configuration structure."""
    console: bool = True
    driver_sources: List[Dict[str, DependencyConfig]
                         ] = field(default_factory=list)
    elements_sources: List[Dict[str, DependencyConfig]
                           ] = field(default_factory=list)
    text_detection: List[Dict[str, DependencyConfig]
                         ] = field(default_factory=list)
    image_detection: List[Dict[str, DependencyConfig]
                          ] = field(default_factory=list)
    file_log: bool = False
    json_log: bool = False
    json_path: Optional[str] = None
    log_level: str = "INFO"
    log_path: Optional[str] = None
    project_path: Optional[str] = None

    def __post_init__(self):
        if not self.driver_sources:
            self.driver_sources = [
                {"appium": DependencyConfig(
                    enabled=False,
                    url="http://127.0.0.1:4723",
                    capabilities={
                        "deviceName": None,
                        "platformName": None,
                        "automationName": None,
                        "appPackage": None,
                        "appActivity": None
                    }
                )},
                {"ble": DependencyConfig(
                    enabled=False, url=None, capabilities={})}
            ]
        if not self.elements_sources:
            self.elements_sources = [
                {"appium_find_element": DependencyConfig(
                    enabled=True, url=None, capabilities={})},
                {"appium_page_source": DependencyConfig(
                    enabled=False, url=None, capabilities={})},
                {"device_screenshot": DependencyConfig(
                    enabled=False, url=None, capabilities={})},
                {"webcam_screenshot": DependencyConfig(
                    enabled=False, url=None, capabilities={})}
            ]
        if not self.text_detection:
            self.text_detection = [
                {"easyocr": DependencyConfig(
                    enabled=False, url=None, capabilities={})},
                {"pytesseract": DependencyConfig(
                    enabled=False, url=None, capabilities={})},
                {"google_vision": DependencyConfig(
                    enabled=False, url=None, capabilities={})}
            ]
        if not self.image_detection:
            self.image_detection = [
                {"templatematch": DependencyConfig(
                    enabled=False, url=None, capabilities={})}
            ]


class ConfigHandler:
    _instance = None
    _initialized = False
    DEFAULT_GLOBAL_CONFIG = os.path.expanduser("~/.optics/global_config.yaml")
    DEPENDENCY_KEYS: List[str] = [
        "driver_sources",
        "elements_sources",
        "text_detection",
        "image_detection"
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.project_name: Optional[str] = None
            self.project_config_path: Optional[str] = None
            self.global_config_path: str = self.DEFAULT_GLOBAL_CONFIG
            self.config: Config = Config()
            # Changed to store lists of names
            self._enabled_configs: Dict[str, List[str]] = {}
            self._initialized = True

    def set_project(self, project_name: str) -> None:
        self.project_name = project_name
        self.project_config_path = os.path.join(
            project_name, "config.yaml") if project_name else None
        self.config.project_path = self.get_project_path()

    def get_project_path(self) -> Optional[str]:
        return os.path.dirname(self.project_config_path) if self.project_config_path else None

    def _ensure_global_config(self) -> None:
        if not os.path.exists(self.global_config_path):
            os.makedirs(os.path.dirname(
                self.global_config_path), exist_ok=True)
            with open(self.global_config_path, "w", encoding="utf-8") as f:
                yaml.dump(asdict(self.config), f, default_flow_style=False)

    def load(self) -> Config:
        global_config = self._load_yaml(self.global_config_path) or {}
        project_config = self._load_yaml(
            self.project_config_path) if self.project_config_path else {}
        default_dict = asdict(self.config)
        merged = deep_merge(default_dict, global_config)
        merged = deep_merge(merged, project_config)
        self.config = Config(**merged)
        self._precompute_enabled_configs()
        return self.config

    def _load_yaml(self, path: str) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                logging.error(f"Error parsing YAML file {path}: {e}")
                return {}
        return {}

    def _precompute_enabled_configs(self) -> None:
        for key in self.DEPENDENCY_KEYS:
            value = getattr(self.config, key)
            enabled_names = []
            for item in value:
                for name, details in item.items():
                    if isinstance(details, dict) and details.get("enabled", False):
                        enabled_names.append(name)
            self._enabled_configs[key] = enabled_names  # Store just the names

    def get_dependency_config(self, dependency_type: str, name: str) -> Optional[Dict[str, Any]]:
        # Still available if detailed config is needed elsewhere
        for item in getattr(self.config, dependency_type):
            if name in item and item[name].get("enabled", False):
                return {
                    "url": item[name].get("url"),
                    "capabilities": item[name].get("capabilities", {})
                }
        return None

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.DEPENDENCY_KEYS:
            return self._enabled_configs.get(key, default if default is not None else [])
        return getattr(self.config, key, default)

    def save_config(self) -> None:
        try:
            with open(self.global_config_path, "w", encoding="utf-8") as f:
                yaml.dump(asdict(self.config), f, default_flow_style=False)
        except Exception as e:
            raise e

    @classmethod
    def get_instance(cls) -> 'ConfigHandler':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
