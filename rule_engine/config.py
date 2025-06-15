# Configuration system for rule engine
import yaml
import os
from typing import Dict, Any, List

# Default configuration
DEFAULT_CONFIG = {
    "rules": {
        "python": {
            "python_naming_convention": {"enabled": True, "severity": "medium"},
            "python_unused_import": {"enabled": True, "severity": "low"},
            "python_except_pass": {"enabled": True, "severity": "high"},
            "python_sql_injection": {"enabled": True, "severity": "critical"},
            "python_nested_loop": {"enabled": True, "severity": "medium"}
        },
        "javascript": {
            "javascript_var_usage": {"enabled": True, "severity": "medium"},
            "javascript_equality": {"enabled": True, "severity": "high"},
            "javascript_eval": {"enabled": True, "severity": "critical"},
            "javascript_array_foreach": {"enabled": True, "severity": "low"}
        }
    },
    "categories": {
        "quality": {"enabled": True},
        "bug": {"enabled": True},
        "security": {"enabled": True},
        "performance": {"enabled": True},
        "style": {"enabled": True},
        "maintainability": {"enabled": True}
    },
    "severity_levels": ["critical", "high", "medium", "low"],
    "rating_weights": {
        "critical": 2.0,
        "high": 1.0,
        "medium": 0.5,
        "low": 0.2
    }
}

class RuleConfig:
    def __init__(self, config_path: str = None):
        self.config = DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config and isinstance(user_config, dict):
                    # Merge user config with default config
                    self._merge_configs(self.config, user_config)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
    
    def _merge_configs(self, default_config: Dict[str, Any], user_config: Dict[str, Any]) -> None:
        """Recursively merge user config into default config"""
        for key, value in user_config.items():
            if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                self._merge_configs(default_config[key], value)
            else:
                default_config[key] = value
    
    def save_config(self, config_path: str) -> None:
        """Save current configuration to YAML file"""
        try:
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {str(e)}")
    
    def is_rule_enabled(self, rule_name: str, language: str) -> bool:
        """Check if a rule is enabled for a specific language"""
        if language.lower() in self.config["rules"] and rule_name in self.config["rules"][language.lower()]:
            return self.config["rules"][language.lower()][rule_name]["enabled"]
        return True  # Default to enabled if not specified
    
    def get_rule_severity(self, rule_name: str, language: str, default_severity: str) -> str:
        """Get the configured severity for a rule"""
        if language.lower() in self.config["rules"] and rule_name in self.config["rules"][language.lower()]:
            return self.config["rules"][language.lower()][rule_name]["severity"]
        return default_severity
    
    def is_category_enabled(self, category: str) -> bool:
        """Check if a rule category is enabled"""
        if category in self.config["categories"]:
            return self.config["categories"][category]["enabled"]
        return True  # Default to enabled if not specified
    
    def get_rating_weight(self, severity: str) -> float:
        """Get the rating weight for a severity level"""
        return self.config["rating_weights"].get(severity.lower(), 0.2)
    
    def get_enabled_rules(self, language: str) -> List[str]:
        """Get a list of enabled rule names for a specific language"""
        if language.lower() in self.config["rules"]:
            return [rule for rule, settings in self.config["rules"][language.lower()].items() 
                   if settings["enabled"]]
        return []