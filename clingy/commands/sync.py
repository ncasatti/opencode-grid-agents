#!/usr/bin/env python3
"""
Sync Command

Sync local folders with cloud storage using rclone.
"""

import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from config import (
    KONFIG_PATH,
    OBSIDIAN_VAULT_PATH,
    RCLONE_KONFIG_PATH,
    RCLONE_OBSIDIAN_PATH,
    RCLONE_REMOTE,
)
from core.status import resolve_konfig_path

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


class SyncCommand(BaseCommand):
    """Sync local folders with cloud storage using rclone"""

    name = "sync"
    help = "Sync folders with cloud storage"
    description = "Sync local folders (Obsidian vault, etc.) with cloud storage using rclone"

    def add_arguments(self, parser: ArgumentParser):
        """Add command-specific arguments"""
        parser.add_argument(
            "--upload",
            action="store_true",
            help="Upload local files to cloud",
        )
        parser.add_argument(
            "--download",
            action="store_true",
            help="Download cloud files to local",
        )
        parser.add_argument(
            "--obsidian",
            action="store_true",
            help="Sync Obsidian vault",
        )
        parser.add_argument(
            "--konfig",
            action="store_true",
            help="Sync Konfig dotfiles",
        )

    def execute(self, args: Namespace) -> bool:
        """Execute sync action (CLI mode)"""
        if args.obsidian:
            if args.upload:
                return self._sync_obsidian(upload=True)
            elif args.download:
                return self._sync_obsidian(upload=False)
            else:
                log_error("Specify --upload or --download")
                return False

        if args.konfig:
            if args.upload:
                return self._sync_konfig(upload=True)
            elif args.download:
                return self._sync_konfig(upload=False)
            else:
                log_error("Specify --upload or --download")
                return False

        log_info("Use interactive menu: manager")
        return True

    def get_menu_tree(self) -> MenuNode:
        """Build interactive menu tree"""
        return MenuNode(
            label="Sync",
            emoji=Emoji.SYNC,
            children=[
                MenuNode(
                    label="Obsidian Vault",
                    emoji=Emoji.DOCUMENT,
                    children=[
                        MenuNode(
                            label="Upload (Local → Cloud)",
                            emoji=Emoji.UPLOAD,
                            action=self._sync_obsidian,
                            action_kwargs={"upload": True},
                        ),
                        MenuNode(
                            label="Download (Cloud → Local)",
                            emoji=Emoji.DOWNLOAD,
                            action=self._sync_obsidian,
                            action_kwargs={"upload": False},
                        ),
                    ],
                ),
                MenuNode(
                    label="Konfig Dotfiles",
                    emoji=Emoji.GEAR,
                    children=[
                        MenuNode(
                            label="Upload (Local → Cloud)",
                            emoji=Emoji.UPLOAD,
                            action=self._sync_konfig,
                            action_kwargs={"upload": True},
                        ),
                        MenuNode(
                            label="Download (Cloud → Local)",
                            emoji=Emoji.DOWNLOAD,
                            action=self._sync_konfig,
                            action_kwargs={"upload": False},
                        ),
                    ],
                ),
            ],
        )

    def _sync_obsidian(self, upload: bool) -> bool:
        """
        Sync Obsidian vault with cloud storage using rclone.

        Args:
            upload: True to upload (local → cloud), False to download (cloud → local)

        Returns:
            True if sync succeeded, False otherwise
        """
        # Expand paths
        local_path = Path(OBSIDIAN_VAULT_PATH).expanduser()
        remote_path = f"{RCLONE_REMOTE}:{RCLONE_OBSIDIAN_PATH}"

        # Validate local path exists
        if not local_path.exists():
            log_error(f"Obsidian vault not found: {local_path}")
            log_info("Edit config.py and set OBSIDIAN_VAULT_PATH to your vault location")
            return False

        # Check if rclone is installed
        try:
            result = subprocess.run(["rclone", "version"], capture_output=True, check=True)
        except FileNotFoundError:
            log_error("rclone is not installed")
            log_info("Install with: curl https://rclone.org/install.sh | sudo bash")
            return False
        except subprocess.CalledProcessError:
            log_error("rclone is installed but not working correctly")
            return False

        # Build rclone command
        if upload:
            # Upload: local → cloud
            source = str(local_path)
            destination = remote_path
            direction = "UPLOAD (Local → Cloud)"
        else:
            # Download: cloud → local
            source = remote_path
            destination = str(local_path)
            direction = "DOWNLOAD (Cloud → Local)"

        command = [
            "rclone",
            "sync",
            source,
            destination,
            "-P",  # Show progress
            "--checkers=8",  # Parallel file checks
            "--transfers=4",  # Parallel transfers
        ]

        # Log operation
        log_section(f"SYNCING OBSIDIAN VAULT - {direction}")
        log_info(f"Source:      {source}")
        log_info(f"Destination: {destination}")
        log_info(f"Command:     {' '.join(command)}")
        log_warning("This will sync files (overwrite destination if different)")

        # Execute rclone sync
        try:
            result = subprocess.run(command, check=True, text=True)

            if result.returncode == 0:
                log_success(f"Obsidian vault synced successfully ({direction})")
                return True
            else:
                log_error(f"Sync failed with code {result.returncode}")
                return False

        except subprocess.CalledProcessError as e:
            log_error(f"Sync failed: {e}")
            return False
        except KeyboardInterrupt:
            log_warning("Sync cancelled by user")
            return False

    def _sync_konfig(self, upload: bool) -> bool:
        """
        Sync Konfig dotfiles with cloud storage using rclone.

        Args:
            upload: True to upload (local → cloud), False to download (cloud → local)

        Returns:
            True if sync succeeded, False otherwise
        """
        # Expand paths
        local_path = resolve_konfig_path(KONFIG_PATH)
        remote_path = f"{RCLONE_REMOTE}:{RCLONE_KONFIG_PATH}"

        # Validate local path exists
        if not local_path.exists():
            log_error(f"Konfig directory not found: {local_path}")
            log_info("Edit config.py and set KONFIG_PATH to your dotfiles location")
            return False

        # Check if rclone is installed
        try:
            result = subprocess.run(["rclone", "version"], capture_output=True, check=True)
        except FileNotFoundError:
            log_error("rclone is not installed")
            log_info("Install with: curl https://rclone.org/install.sh | sudo bash")
            return False
        except subprocess.CalledProcessError:
            log_error("rclone is installed but not working correctly")
            return False

        # Build rclone command
        if upload:
            # Upload: local → cloud
            source = str(local_path)
            destination = remote_path
            direction = "UPLOAD (Local → Cloud)"
        else:
            # Download: cloud → local
            source = remote_path
            destination = str(local_path)
            direction = "DOWNLOAD (Cloud → Local)"

        command = [
            "rclone",
            "sync",
            source,
            destination,
            "-P",  # Show progress
            "--copy-links",  # Follow symlinks (importante para dotfiles)
            "--checkers=8",  # Parallel file checks
            "--transfers=4",  # Parallel transfers
        ]

        # Log operation
        log_section(f"SYNCING KONFIG DOTFILES - {direction}")
        log_info(f"Source:      {source}")
        log_info(f"Destination: {destination}")
        log_info(f"Command:     {' '.join(command)}")
        log_warning("This will sync files (overwrite destination if different)")

        # Execute rclone sync
        try:
            result = subprocess.run(command, check=True, text=True)

            if result.returncode == 0:
                log_success(f"Konfig dotfiles synced successfully ({direction})")
                return True
            else:
                log_error(f"Sync failed with code {result.returncode}")
                return False

        except subprocess.CalledProcessError as e:
            log_error(f"Sync failed: {e}")
            return False
        except KeyboardInterrupt:
            log_warning("Sync cancelled by user")
            return False
