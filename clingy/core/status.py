#!/usr/bin/env python3
"""
Status Checking and Summaries

Functions for checking configuration status and generating summaries.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from core.link_core import LinkStatus, get_link_status, requires_sudo
from core.models import Config, load_mappings

from clingy.core.discovery import find_clingy_root

CONFIGS, GROUP_DESCRIPTIONS = load_mappings()


def resolve_konfig_path(path_str: str) -> Path:
    """
    Resolve KONFIG_PATH to an absolute Path.
    If it's relative, resolve it relative to the project root.

    Args:
        path_str: Path string from config

    Returns:
        Resolved absolute Path object
    """
    path = Path(os.path.expanduser(os.path.expandvars(path_str)))
    if not path.is_absolute():
        project_root = find_clingy_root()
        if project_root:
            path = (project_root / path).resolve()
        else:
            path = path.resolve()
    return path


def expand_path(path: str) -> Path:
    """
    Expand path with ~ and environment variables.

    Args:
        path: Path string (may contain ~ or $VAR)

    Returns:
        Expanded Path object
    """
    return Path(os.path.expanduser(os.path.expandvars(path)))


def get_config_status(config: Config, konfig_root: Path) -> Tuple[LinkStatus, str]:
    """
    Get status of a single configuration.

    Args:
        config: Configuration object
        konfig_root: Root path of konfig repository

    Returns:
        Tuple of (LinkStatus, description)
    """
    source = konfig_root / config.source
    target = expand_path(config.target)

    return get_link_status(target, source)


def get_all_statuses(konfig_root: Path) -> Dict[str, Tuple[LinkStatus, str]]:
    """
    Get status of all configurations.

    Args:
        konfig_root: Root path of konfig repository

    Returns:
        Dict mapping config name to (LinkStatus, description)
    """
    statuses = {}
    for config in CONFIGS:
        statuses[config.name] = get_config_status(config, konfig_root)
    return statuses


def get_group_statuses(group: str, konfig_root: Path) -> Dict[str, Tuple[LinkStatus, str]]:
    """
    Get status of all configurations in a group.

    Args:
        group: Group name
        konfig_root: Root path of konfig repository

    Returns:
        Dict mapping config name to (LinkStatus, description)
    """
    statuses = {}
    for config in CONFIGS:
        if config.group == group:
            statuses[config.name] = get_config_status(config, konfig_root)
    return statuses


def get_status_summary(konfig_root: Path) -> Dict[str, int]:
    """
    Get summary counts of all statuses.

    Args:
        konfig_root: Root path of konfig repository

    Returns:
        Dict with counts: {
            'total': int,
            'linked': int,
            'not_linked': int,
            'conflicts': int,
            'wrong_target': int,
            'missing_source': int
        }
    """
    statuses = get_all_statuses(konfig_root)

    summary = {
        "total": len(statuses),
        "linked": 0,
        "not_linked": 0,
        "conflicts": 0,
        "wrong_target": 0,
        "missing_source": 0,
    }

    for status, _ in statuses.values():
        if status == LinkStatus.LINKED:
            summary["linked"] += 1
        elif status == LinkStatus.NOT_LINKED:
            summary["not_linked"] += 1
        elif status == LinkStatus.CONFLICT:
            summary["conflicts"] += 1
        elif status == LinkStatus.WRONG_TARGET:
            summary["wrong_target"] += 1
        elif status == LinkStatus.MISSING_SOURCE:
            summary["missing_source"] += 1

    return summary


def get_group_summary(group: str, konfig_root: Path) -> Dict[str, int]:
    """
    Get summary counts for a specific group.

    Args:
        group: Group name
        konfig_root: Root path of konfig repository

    Returns:
        Dict with counts (same format as get_status_summary)
    """
    statuses = get_group_statuses(group, konfig_root)

    summary = {
        "total": len(statuses),
        "linked": 0,
        "not_linked": 0,
        "conflicts": 0,
        "wrong_target": 0,
        "missing_source": 0,
    }

    for status, _ in statuses.values():
        if status == LinkStatus.LINKED:
            summary["linked"] += 1
        elif status == LinkStatus.NOT_LINKED:
            summary["not_linked"] += 1
        elif status == LinkStatus.CONFLICT:
            summary["conflicts"] += 1
        elif status == LinkStatus.WRONG_TARGET:
            summary["wrong_target"] += 1
        elif status == LinkStatus.MISSING_SOURCE:
            summary["missing_source"] += 1

    return summary


def get_problems(konfig_root: Path) -> List[Tuple[Config, LinkStatus, str]]:
    """
    Get list of configurations with problems (not linked correctly).

    Args:
        konfig_root: Root path of konfig repository

    Returns:
        List of tuples: (Config, LinkStatus, description)
    """
    problems = []

    for config in CONFIGS:
        status, desc = get_config_status(config, konfig_root)
        if status != LinkStatus.LINKED:
            problems.append((config, status, desc))

    return problems


def get_status_icon(status: LinkStatus) -> str:
    """
    Get emoji icon for status.

    Args:
        status: LinkStatus enum

    Returns:
        Emoji string
    """
    icons = {
        LinkStatus.LINKED: "✓",
        LinkStatus.NOT_LINKED: "✗",
        LinkStatus.CONFLICT: "⚠",
        LinkStatus.WRONG_TARGET: "⚠",
        LinkStatus.MISSING_SOURCE: "⚠",
    }
    return icons.get(status, "?")


def get_all_groups() -> List[str]:
    """
    Get list of all unique groups.

    Returns:
        List of group names
    """
    groups = set()
    for config in CONFIGS:
        groups.add(config.group)
    return sorted(list(groups))


def get_configs_by_group(group: str) -> List[Config]:
    """
    Get all configurations in a group.

    Args:
        group: Group name

    Returns:
        List of Config objects
    """
    return [c for c in CONFIGS if c.group == group]


def get_group_description(group: str) -> str:
    """
    Get description for a group.

    Args:
        group: Group name

    Returns:
        Description string
    """
    return GROUP_DESCRIPTIONS.get(group, "")
