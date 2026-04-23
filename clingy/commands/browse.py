#!/usr/bin/env python3
"""
Browse Configurations Command

Interactive navigation through configuration groups with fzf.
"""

import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from config import KONFIG_PATH
from core.link_core import (
    LinkStatus,
    auto_copy_from_system,
    create_backup,
    create_link,
    remove_link,
    requires_sudo,
)
from core.status import (
    expand_path,
    get_all_groups,
    get_config_status,
    get_configs_by_group,
    get_group_description,
    get_status_icon,
    resolve_konfig_path,
)

from clingy.commands.base import BaseCommand
from clingy.core.logger import log_error, log_info, log_success, log_warning
from clingy.core.menu import MenuNode


class BrowseCommand(BaseCommand):
    """Browse and manage configurations by group"""

    name = "browse"
    help = "Browse configurations by group"
    description = "Interactive navigation through configuration groups with status display"

    def add_arguments(self, parser: ArgumentParser):
        """Add command-specific arguments"""
        parser.add_argument("--group", help="Specific group to browse", choices=get_all_groups())

    def execute(self, args: Namespace) -> bool:
        """Execute browse command (CLI mode)"""
        # In CLI mode, just show the menu
        return True

    def get_menu_tree(self) -> MenuNode:
        """Build interactive menu tree"""
        konfig_root = resolve_konfig_path(KONFIG_PATH)

        if not konfig_root.exists():
            log_error(f"Konfig path not found: {konfig_root}")
            log_info("Edit config.py and set KONFIG_PATH to your dotfiles repository")
            return MenuNode(label="Error: Konfig path not found")

        # Build group menus
        group_nodes = []
        for group in get_all_groups():
            group_desc = get_group_description(group)
            configs = get_configs_by_group(group)

            # Build config items for this group
            config_nodes = []
            for config in configs:
                # Create submenu for each config with dynamic labels
                config_nodes.append(
                    MenuNode(
                        label_generator=self._get_config_label,
                        label_args=(config, konfig_root),
                        children=[
                            MenuNode(
                                label_generator=self._get_status_label,
                                label_args=(config, konfig_root),
                                action=self._show_config_info,
                                action_args=(config, konfig_root),
                            ),
                            MenuNode(
                                label="Link",
                                action=self._link_config,
                                action_args=(config, konfig_root),
                            ),
                            MenuNode(
                                label="Unlink",
                                action=self._unlink_config,
                                action_args=(config, konfig_root),
                            ),
                        ],
                    )
                )

            # Add group-level actions
            config_nodes.extend(
                [
                    MenuNode(label="───────────────"),  # Separator
                    MenuNode(
                        label="Link All in Group",
                        action=self._link_group,
                        action_args=(group, konfig_root),
                    ),
                    MenuNode(
                        label="Unlink All in Group",
                        action=self._unlink_group,
                        action_args=(group, konfig_root),
                    ),
                ]
            )

            # Create group node
            group_label = f"📁 {group.title()}"
            if group_desc:
                group_label += f" - {group_desc}"

            group_nodes.append(MenuNode(label=group_label, children=config_nodes))

        return MenuNode(label="Browse Configurations", emoji="🔍", children=group_nodes)

    def _show_config_info(self, config, konfig_root: Path) -> bool:
        """Show detailed info about a configuration"""
        source = konfig_root / config.source
        target = expand_path(config.target)
        status, desc = get_config_status(config, konfig_root)

        log_info(f"Configuration: {config.get_display_name()}")
        log_info(f"  Name: {config.name}")
        log_info(f"  Group: {config.group}")
        log_info(f"  Source: {source}")
        log_info(f"  Target: {target}")
        log_info(f"  Status: {desc}")
        log_info(f"  Requires sudo: {requires_sudo(target)}")

        return True

    def _link_config(self, config, konfig_root: Path) -> bool:
        """Link a single configuration"""
        source = konfig_root / config.source
        target = expand_path(config.target)
        needs_sudo = requires_sudo(target)

        # Check current status
        status, desc = get_config_status(config, konfig_root)

        if status == LinkStatus.LINKED:
            log_success(f"{config.get_display_name()}: Already correctly linked")
            return True

        # Auto-copy if source missing
        if status == LinkStatus.MISSING_SOURCE:
            log_info(f"{config.get_display_name()}: Auto-copying from system...")
            if not auto_copy_from_system(source, target, needs_sudo):
                log_error(f"{config.get_display_name()}: Failed to copy from system")
                return False
            log_success(f"{config.get_display_name()}: Copied from system")

        # Handle conflicts
        if status == LinkStatus.CONFLICT:
            log_warning(f"{config.get_display_name()}: File exists, creating backup...")
            if not create_backup(target, needs_sudo):
                log_error(f"{config.get_display_name()}: Failed to create backup")
                return False

        # Remove wrong symlink
        if status == LinkStatus.WRONG_TARGET:
            log_info(f"{config.get_display_name()}: Removing wrong symlink...")
            if not remove_link(target, needs_sudo):
                log_error(f"{config.get_display_name()}: Failed to remove wrong symlink")
                return False

        # Create link
        if create_link(source, target, needs_sudo):
            log_success(f"{config.get_display_name()}: Linked successfully")
            return True
        else:
            log_error(f"{config.get_display_name()}: Failed to create link")
            return False

    def _unlink_config(self, config, konfig_root: Path) -> bool:
        """Unlink a single configuration"""
        target = expand_path(config.target)
        needs_sudo = requires_sudo(target)

        # Check current status
        status, desc = get_config_status(config, konfig_root)

        if status == LinkStatus.NOT_LINKED:
            log_info(f"{config.get_display_name()}: Already not linked")
            return True

        if status != LinkStatus.LINKED and status != LinkStatus.WRONG_TARGET:
            log_warning(f"{config.get_display_name()}: Not a symlink, skipping")
            return False

        # Remove link
        if remove_link(target, needs_sudo):
            log_success(f"{config.get_display_name()}: Unlinked successfully")
            return True
        else:
            log_error(f"{config.get_display_name()}: Failed to unlink")
            return False

    def _link_group(self, group: str, konfig_root: Path) -> bool:
        """Link all configurations in a group"""
        configs = get_configs_by_group(group)

        log_info(f"Linking all configurations in group: {group}")

        success_count = 0
        fail_count = 0

        for config in configs:
            if self._link_config(config, konfig_root):
                success_count += 1
            else:
                fail_count += 1

        log_info(f"Group {group}: {success_count} linked, {fail_count} failed")
        return fail_count == 0

    def _unlink_group(self, group: str, konfig_root: Path) -> bool:
        """Unlink all configurations in a group"""
        configs = get_configs_by_group(group)

        log_info(f"Unlinking all configurations in group: {group}")

        success_count = 0
        fail_count = 0

        for config in configs:
            if self._unlink_config(config, konfig_root):
                success_count += 1
            else:
                fail_count += 1

        log_info(f"Group {group}: {success_count} unlinked, {fail_count} failed")
        return fail_count == 0

    def _get_config_label(self, config, konfig_root: Path) -> str:
        """Generate dynamic label for config with current status icon"""
        status, _ = get_config_status(config, konfig_root)
        icon = get_status_icon(status)
        return f"{icon} {config.get_display_name()}"

    def _get_status_label(self, config, konfig_root: Path) -> str:
        """Generate dynamic status label"""
        _, desc = get_config_status(config, konfig_root)
        return f"Status: {desc}"
