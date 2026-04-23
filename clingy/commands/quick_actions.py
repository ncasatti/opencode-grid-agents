#!/usr/bin/env python3
"""
Quick Actions Command

Fast actions for common operations (link all, unlink all, status summary).
"""

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
from core.models import load_mappings
from core.status import (
    expand_path,
    get_all_statuses,
    get_config_status,
    get_problems,
    get_status_icon,
    get_status_summary,
    resolve_konfig_path,
)

CONFIGS, _ = load_mappings()

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import (
    log_error,
    log_info,
    log_section,
    log_success,
    log_warning,
)
from clingy.core.menu import MenuNode


class QuickActionsCommand(BaseCommand):
    """Quick actions for common operations"""

    name = "quick"
    help = "Quick actions (link all, unlink all, status)"
    description = "Fast actions for common configuration management tasks"

    def add_arguments(self, parser: ArgumentParser):
        """Add command-specific arguments"""
        parser.add_argument(
            "--action",
            choices=["link-all", "unlink-all", "status", "verify"],
            help="Action to perform",
        )

    def execute(self, args: Namespace) -> bool:
        """Execute quick action (CLI mode)"""
        if not args.action:
            log_error("No action specified. Use --action")
            return False

        konfig_root = resolve_konfig_path(KONFIG_PATH)

        if args.action == "link-all":
            return self._link_all(konfig_root)
        elif args.action == "unlink-all":
            return self._unlink_all(konfig_root)
        elif args.action == "status":
            return self._show_status_summary(konfig_root)
        elif args.action == "verify":
            return self._verify_integrity(konfig_root)

        return False

    def get_menu_tree(self) -> MenuNode:
        """Build interactive menu tree"""
        konfig_root = resolve_konfig_path(KONFIG_PATH)

        if not konfig_root.exists():
            log_error(f"Konfig path not found: {konfig_root}")
            log_info("Edit config.py and set KONFIG_PATH to your dotfiles repository")
            return MenuNode(label="Error: Konfig path not found")

        return MenuNode(
            label="Quick Actions",
            emoji=Emoji.QUICK_ACTIONS,
            children=[
                MenuNode(
                    label="Link All Configurations",
                    emoji=Emoji.LINK,
                    action=self._link_all,
                    action_args=(konfig_root,),
                ),
                MenuNode(
                    label="Unlink All Configurations",
                    emoji=Emoji.UNLINK,
                    action=self._unlink_all,
                    action_args=(konfig_root,),
                ),
                MenuNode(
                    label="Show Status Summary",
                    emoji=Emoji.STATS,
                    action=self._show_status_summary,
                    action_args=(konfig_root,),
                ),
                MenuNode(
                    label="Verify Integrity",
                    emoji=Emoji.SEARCH,
                    action=self._verify_integrity,
                    action_args=(konfig_root,),
                ),
            ],
        )

    def _link_all(self, konfig_root: Path) -> bool:
        """Link all configurations"""
        log_section("LINKING ALL CONFIGURATIONS")

        success_count = 0
        fail_count = 0
        skip_count = 0

        for config in CONFIGS:
            source = konfig_root / config.source
            target = expand_path(config.target)
            needs_sudo = requires_sudo(target)

            # Check current status
            status, desc = get_config_status(config, konfig_root)

            if status == LinkStatus.LINKED:
                skip_count += 1
                continue

            # Auto-copy if source missing
            if status == LinkStatus.MISSING_SOURCE:
                log_info(f"{config.get_display_name()}: Auto-copying from system...")
                if not auto_copy_from_system(source, target, needs_sudo):
                    log_error(f"{config.get_display_name()}: Failed to copy")
                    fail_count += 1
                    continue

            # Handle conflicts
            if status == LinkStatus.CONFLICT:
                if not create_backup(target, needs_sudo):
                    log_error(f"{config.get_display_name()}: Failed to backup")
                    fail_count += 1
                    continue

            # Remove wrong symlink
            if status == LinkStatus.WRONG_TARGET:
                if not remove_link(target, needs_sudo):
                    log_error(f"{config.get_display_name()}: Failed to remove wrong link")
                    fail_count += 1
                    continue

            # Create link
            if create_link(source, target, needs_sudo):
                log_success(f"{config.get_display_name()}: Linked")
                success_count += 1
            else:
                log_error(f"{config.get_display_name()}: Failed to link")
                fail_count += 1

        log_section("SUMMARY")
        log_info(f"Total: {len(CONFIGS)}")
        log_success(f"Linked: {success_count}")
        log_info(f"Already linked: {skip_count}")
        if fail_count > 0:
            log_error(f"Failed: {fail_count}")

        return fail_count == 0

    def _unlink_all(self, konfig_root: Path) -> bool:
        """Unlink all configurations"""
        log_section("UNLINKING ALL CONFIGURATIONS")

        success_count = 0
        fail_count = 0
        skip_count = 0

        for config in CONFIGS:
            target = expand_path(config.target)
            needs_sudo = requires_sudo(target)

            # Check current status
            status, desc = get_config_status(config, konfig_root)

            if status == LinkStatus.NOT_LINKED:
                skip_count += 1
                continue

            if status != LinkStatus.LINKED and status != LinkStatus.WRONG_TARGET:
                log_warning(f"{config.get_display_name()}: Not a symlink, skipping")
                skip_count += 1
                continue

            # Remove link
            if remove_link(target, needs_sudo):
                log_success(f"{config.get_display_name()}: Unlinked")
                success_count += 1
            else:
                log_error(f"{config.get_display_name()}: Failed to unlink")
                fail_count += 1

        log_section("SUMMARY")
        log_info(f"Total: {len(CONFIGS)}")
        log_success(f"Unlinked: {success_count}")
        log_info(f"Already unlinked: {skip_count}")
        if fail_count > 0:
            log_error(f"Failed: {fail_count}")

        return fail_count == 0

    def _show_status_summary(self, konfig_root: Path) -> bool:
        """Show status summary"""
        log_section("STATUS SUMMARY")

        summary = get_status_summary(konfig_root)

        log_info(f"Total configurations: {summary['total']}")
        log_success(f"✓ Linked: {summary['linked']}")
        log_info(f"✗ Not linked: {summary['not_linked']}")

        if summary["conflicts"] > 0:
            log_warning(f"⚠ Conflicts: {summary['conflicts']}")
        if summary["wrong_target"] > 0:
            log_warning(f"⚠ Wrong target: {summary['wrong_target']}")
        if summary["missing_source"] > 0:
            log_warning(f"⚠ Missing source: {summary['missing_source']}")

        # Show percentage
        if summary["total"] > 0:
            percentage = (summary["linked"] / summary["total"]) * 100
            log_info(f"Coverage: {percentage:.1f}%")

        return True

    def _verify_integrity(self, konfig_root: Path) -> bool:
        """Verify integrity and show problems"""
        log_section("VERIFYING INTEGRITY")

        problems = get_problems(konfig_root)

        if not problems:
            log_success("All configurations are correctly linked!")
            return True

        log_warning(f"Found {len(problems)} problem(s):")

        for config, status, desc in problems:
            icon = get_status_icon(status)
            log_info(f"{icon} {config.get_display_name()}: {desc}")

        return False
