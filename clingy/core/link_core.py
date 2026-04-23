#!/usr/bin/env python3
"""
Core Linking Logic

Pure functions for symlink management (extracted from symlink_manager.py).
"""

import shutil
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Tuple


class LinkStatus(Enum):
    """Symlink status enumeration."""

    LINKED = "linked"  # Correctly linked
    NOT_LINKED = "not_linked"  # Target doesn't exist
    CONFLICT = "conflict"  # Target exists but not a symlink
    WRONG_TARGET = "wrong_target"  # Symlink points to wrong location
    MISSING_SOURCE = "missing_source"  # Source doesn't exist in konfig


def requires_sudo(path: Path) -> bool:
    """
    Check if path requires sudo access.

    Args:
        path: Path to check

    Returns:
        True if path requires sudo
    """
    from config import SUDO_PATHS

    return any(str(path).startswith(p) for p in SUDO_PATHS)


def is_correct_symlink(target: Path, source: Path) -> bool:
    """
    Check if target is a symlink pointing to the correct source.

    Args:
        target: System path (e.g., ~/.config/nvim)
        source: Konfig path (e.g., ~/.config/konfig/nvim)

    Returns:
        True if target is correctly linked to source
    """
    if target.is_symlink():
        current_target = target.resolve()
        expected_target = source.resolve()
        return current_target == expected_target
    return False


def get_link_status(target: Path, source: Path) -> Tuple[LinkStatus, str]:
    """
    Get detailed status of a symlink.

    Args:
        target: System path
        source: Konfig path

    Returns:
        Tuple of (LinkStatus, description)
    """
    # Check if source exists
    if not source.exists():
        return LinkStatus.MISSING_SOURCE, f"Source missing: {source}"

    # Check if target doesn't exist
    if not target.exists():
        return LinkStatus.NOT_LINKED, "Not linked"

    # Check if correctly linked
    if is_correct_symlink(target, source):
        return LinkStatus.LINKED, "Correctly linked"

    # Check if symlink to wrong target
    if target.is_symlink():
        actual_target = target.readlink()
        return LinkStatus.WRONG_TARGET, f"Wrong target: {actual_target}"

    # Regular file/directory (conflict)
    return LinkStatus.CONFLICT, "File/directory exists (not linked)"


def run_with_sudo(cmd: list, dry_run: bool = False) -> bool:
    """
    Run command with sudo.

    Args:
        cmd: Command to run
        dry_run: If True, only print what would be done

    Returns:
        True if successful
    """
    try:
        if dry_run:
            print(f"[DRY RUN] Would run with sudo: {' '.join(cmd)}")
            return True

        result = subprocess.run(["sudo"] + cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def create_backup(target: Path, needs_sudo: bool = False, dry_run: bool = False) -> bool:
    """
    Create backup of existing file/directory.

    Args:
        target: Path to backup
        needs_sudo: Whether sudo is required
        dry_run: If True, only print what would be done

    Returns:
        True if successful
    """
    from config import BACKUP_SUFFIX, BACKUP_TIMESTAMP_FORMAT

    timestamp = datetime.now().strftime(BACKUP_TIMESTAMP_FORMAT)
    backup_path = Path(f"{target}{BACKUP_SUFFIX}.{timestamp}")

    if dry_run:
        print(f"[DRY RUN] Would backup {target} → {backup_path}")
        return True

    try:
        if needs_sudo:
            return run_with_sudo(["mv", str(target), str(backup_path)])
        else:
            target.rename(backup_path)
            return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False


def auto_copy_from_system(
    source: Path, target: Path, needs_sudo: bool = False, dry_run: bool = False
) -> bool:
    """
    Auto-copy file/directory from system to konfig if source doesn't exist.

    Args:
        source: Konfig path (destination)
        target: System path (source to copy from)
        needs_sudo: Whether sudo is required
        dry_run: If True, only print what would be done

    Returns:
        True if successful
    """
    if source.exists():
        return True  # Source already exists

    if not target.exists():
        return False  # Nothing to copy

    if dry_run:
        print(f"[DRY RUN] Would copy {target} → {source}")
        return True

    try:
        # Create parent directory
        source.parent.mkdir(parents=True, exist_ok=True)

        if needs_sudo:
            if target.is_dir():
                return run_with_sudo(["cp", "-r", str(target), str(source)])
            else:
                return run_with_sudo(["cp", str(target), str(source)])
        else:
            if target.is_dir():
                shutil.copytree(target, source)
            else:
                shutil.copy2(target, source)
            return True
    except Exception as e:
        print(f"Error copying from system: {e}")
        return False


def create_link(
    source: Path, target: Path, needs_sudo: bool = False, dry_run: bool = False
) -> bool:
    """
    Create symlink from target to source.

    Args:
        source: Konfig path (what the symlink points to)
        target: System path (where the symlink is created)
        needs_sudo: Whether sudo is required
        dry_run: If True, only print what would be done

    Returns:
        True if successful
    """
    if dry_run:
        print(f"[DRY RUN] Would create symlink: {target} → {source}")
        return True

    try:
        # Create parent directory if needed
        if needs_sudo:
            run_with_sudo(["mkdir", "-p", str(target.parent)])
        else:
            target.parent.mkdir(parents=True, exist_ok=True)

        # Create symlink
        if needs_sudo:
            return run_with_sudo(["ln", "-sf", str(source), str(target)])
        else:
            target.symlink_to(source)
            return True
    except Exception as e:
        print(f"Error creating symlink: {e}")
        return False


def remove_link(target: Path, needs_sudo: bool = False, dry_run: bool = False) -> bool:
    """
    Remove symlink (only if it's actually a symlink).

    Args:
        target: System path
        needs_sudo: Whether sudo is required
        dry_run: If True, only print what would be done

    Returns:
        True if successful
    """
    if not target.exists():
        return True  # Already removed

    if not target.is_symlink():
        print(f"Warning: {target} is not a symlink, skipping removal")
        return False

    if dry_run:
        print(f"[DRY RUN] Would remove symlink: {target}")
        return True

    try:
        if needs_sudo:
            return run_with_sudo(["rm", str(target)])
        else:
            target.unlink()
            return True
    except Exception as e:
        print(f"Error removing symlink: {e}")
        return False
