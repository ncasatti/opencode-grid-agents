#!/usr/bin/env python3
"""
Status Command

Detailed status display with tables and group summaries.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from config import KONFIG_PATH
from core.status import (
    expand_path,
    get_all_groups,
    get_all_statuses,
    get_config_status,
    get_configs_by_group,
    get_group_summary,
    get_status_icon,
    resolve_konfig_path,
)

from clingy.commands.base import BaseCommand
from clingy.core.logger import log_error, log_info, log_section
from clingy.core.menu import MenuNode


class StatusCommand(BaseCommand):
    """Show detailed status of all configurations"""

    name = "status"
    help = "Show detailed configuration status"
    description = "Display detailed status tables and group summaries"

    def add_arguments(self, parser: ArgumentParser):
        """Add command-specific arguments"""
        parser.add_argument(
            "--group",
            help="Show status for specific group only",
            choices=get_all_groups(),
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed information (paths, etc.)",
        )

    def execute(self, args: Namespace) -> bool:
        """Execute status command"""
        konfig_root = resolve_konfig_path(KONFIG_PATH)

        if not konfig_root.exists():
            log_error(f"Konfig path not found: {konfig_root}")
            log_info("Edit config.py and set KONFIG_PATH to your dotfiles repository")
            return False

        if args.group:
            return self._show_group_status(args.group, konfig_root, args.detailed)
        else:
            return self._show_all_status(konfig_root, args.detailed)

    def get_menu_tree(self) -> MenuNode:
        """Build interactive menu tree"""
        konfig_root = resolve_konfig_path(KONFIG_PATH)

        if not konfig_root.exists():
            log_error(f"Konfig path not found: {konfig_root}")
            return MenuNode(label="Error: Konfig path not found")

        # Build group status menus
        group_nodes = []
        for group in get_all_groups():
            group_nodes.append(
                MenuNode(
                    label=f"Status: {group.title()}",
                    action=self._show_group_status,
                    action_args=(group, konfig_root),
                    action_kwargs={"detailed": True},
                )
            )

        return MenuNode(
            label="Status & Info",
            emoji="📊",
            children=[
                MenuNode(
                    label="Show All Status",
                    action=self._show_all_status,
                    action_args=(konfig_root,),
                    action_kwargs={"detailed": False},
                ),
                MenuNode(
                    label="Show All Status (Detailed)",
                    action=self._show_all_status,
                    action_args=(konfig_root,),
                    action_kwargs={"detailed": True},
                ),
                MenuNode(label="───────────────"),  # Separator
                *group_nodes,
            ],
        )

    def _show_all_status(self, konfig_root: Path, detailed: bool = False) -> bool:
        """Show status of all configurations"""
        log_section("CONFIGURATION STATUS")

        # Group by status
        for group in get_all_groups():
            self._show_group_status(group, konfig_root, detailed, show_header=False)

        # Show summary
        log_section("SUMMARY BY GROUP")
        for group in get_all_groups():
            summary = get_group_summary(group, konfig_root)
            log_info(
                f"{group.title()}: "
                f"{summary['linked']}/{summary['total']} linked, "
                f"{summary['conflicts']} conflicts, "
                f"{summary['missing_source']} missing"
            )

        return True

    def _show_group_status(
        self,
        group: str,
        konfig_root: Path,
        detailed: bool = False,
        show_header: bool = True,
    ) -> bool:
        """Show status for a specific group"""
        if show_header:
            log_section(f"GROUP: {group.upper()}")
        else:
            log_info(f"\n{group.upper()}:")

        configs = get_configs_by_group(group)

        for config in configs:
            status, desc = get_config_status(config, konfig_root)
            icon = get_status_icon(status)

            if detailed:
                source = konfig_root / config.source
                target = expand_path(config.target)
                log_info(f"{icon} {config.get_display_name()}")
                log_info(f"    Status: {desc}")
                log_info(f"    Source: {source}")
                log_info(f"    Target: {target}")
            else:
                log_info(f"{icon} {config.get_display_name()}: {desc}")

        # Show group summary
        summary = get_group_summary(group, konfig_root)
        log_info(f"  → {summary['linked']}/{summary['total']} linked")

        return True
