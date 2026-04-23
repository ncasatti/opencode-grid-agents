#!/usr/bin/env python3
"""
Konfig Template Configuration

Configuration for dotfiles symlink management.
"""

# Project metadata
PROJECT_NAME = "Konfig Manager"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "Interactive dotfiles symlink manager with fzf navigation"

# Core paths
KONFIG_PATH = "."  # Path to your dotfiles repository

# Default editor for config editing
DEFAULT_EDITOR = "nvim"

# Backup settings
BACKUP_SUFFIX = ".backup"
BACKUP_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# System paths that require sudo
SUDO_PATHS = ["/etc/", "/usr/", "/opt/", "/var/", "/sys/", "/boot/"]

# Rclone sync settings
RCLONE_REMOTE = "gd"  # Your rclone remote name (run 'rclone listremotes' to see)
RCLONE_OBSIDIAN_PATH = "Docs/Zettelkasten/"  # Path in remote (relative to remote root)
RCLONE_KONFIG_PATH = "Docs/Development/Linux/konfig"  # Path in remote (Konfig dotfiles)

# Obsidian vault settings
OBSIDIAN_VAULT_PATH = "~/Documents/Zettelkasten/"  # Local Obsidian vault path
