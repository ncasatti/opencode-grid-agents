from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import yaml


class Config(NamedTuple):
    """
    Configuration definition using named tuple.

    Args:
        name: Configuration identifier
        source: Path in konfig (relative to konfig root)
        target: System path (absolute or with ~/)
        group: Group name (for organization)
        display_name: Human-readable name (optional)
        requires_sudo: Whether sudo is required (optional, auto-detected)
    """

    name: str
    source: str
    target: str
    group: str
    display_name: Optional[str] = None
    requires_sudo: Optional[bool] = None

    def get_display_name(self):
        """Get display name with fallback to formatted name"""
        return self.display_name or self.name.replace("-", " ").replace("_", " ").title()


def load_mappings() -> Tuple[List[Config], Dict[str, str]]:
    """
    Load YAML configuration mappings.

    Returns:
        Tuple containing (CONFIGS list, GROUP_DESCRIPTIONS dict)
    """
    yaml_path = Path(__file__).parent.parent / "mappings.yaml"
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    group_descriptions = data.get("group_descriptions", {})

    configs = []
    for item in data.get("configs", []):
        configs.append(
            Config(
                name=item["name"],
                source=item["source"],
                target=item["target"],
                group=item["group"],
                display_name=item.get("display_name"),
                requires_sudo=item.get("requires_sudo"),
            )
        )

    return configs, group_descriptions
