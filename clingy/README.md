# Konfig Manager Template

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built with clingy](https://img.shields.io/badge/built%20with-clingy-orange.svg)](https://github.com/ncasatti/clingy)

Interactive symlink manager for Linux dotfiles and system configurations.

## Why Konfig?

Managing dotfiles with manual symlinks or tools like GNU Stow can become cumbersome as your configuration grows. **Konfig** provides a superior experience by offering:

*   **Interactive UI:** Powered by `fzf`, allowing you to browse, search, and manage configurations through a fluid terminal interface.
*   **Conflict Management:** Intelligent detection of existing files or directories, with guided resolution (backup, skip, or overwrite).
*   **Logical Grouping:** Organize your configurations into functional groups (e.g., `shell`, `hyprland`, `themes`) for bulk operations.
*   **Sudo Integration:** Seamlessly handle system-level configurations (e.g., `/etc/keyd`) with automatic elevation prompts.
*   **Status Visibility:** Real-time visual indicators of symlink integrity and configuration state.

## Prerequisites

Before deploying the Konfig template, ensure the following dependencies are present in your environment:

*   **Python 3.8+**: The core execution engine.
*   **fzf**: Required for the interactive fuzzy-search menus.
*   **PyYAML**: Necessary for parsing the configuration mappings.

```bash
# Install dependencies (example for Arch Linux)
sudo pacman -S python fzf python-pyyaml
```

## Architecture

Konfig operates by mapping source files from a central repository to their designated targets in the system.

```text
Central Repository (~/.config/konfig/)          System Environment
├── nvim/                                ---->  ~/.config/nvim/
├── zsh/
│   └── .zshrc                           ---->  ~/.zshrc
└── keyd/
    └── default.conf                     ---->  /etc/keyd/default.conf
```

## Quick Start

### 1. Initialize Project

Create a new directory for your manager and initialize it using the `konfig` template:

```bash
mkdir ~/my-konfig-manager
cd ~/my-konfig-manager
clingy init --template konfig
```

### 2. Configure the Repository Path

Edit `config.py` to define where your source configuration files are stored. 

You can use absolute paths, paths with `~`, or **relative paths**. 
*Relative paths (like `..` or `./dotfiles`) are always resolved relative to your project root (where the `.clingy` file is located), regardless of where you execute the command.*

```python
# Absolute path
KONFIG_PATH = "~/.config/konfig"

# Or relative to the clingy project root
# KONFIG_PATH = ".." 
```

### 3. Define Mappings

Edit `mappings.yaml` to register your configurations. This file replaces the legacy `mappings.py` format.

```yaml
group_descriptions:
  shell: "Terminal and shell environment"
  sudo: "System-level configurations"

configs:
  - name: "nvim"
    source: "nvim"
    target: "~/.config/nvim"
    group: "shell"
    display_name: "Neovim"
  - name: "keyd"
    source: "keyd"
    target: "/etc/keyd"
    group: "sudo"
    requires_sudo: true
```

### 4. Launch the Manager

Execute `clingy` to enter the interactive menu:

```bash
clingy
```

## Configuration Schema

The `mappings.yaml` file follows this structure:

| Field | Description |
|-------|-------------|
| `name` | Unique identifier for the configuration. |
| `source` | Path relative to `KONFIG_PATH`. |
| `target` | Absolute path (or `~` prefixed) where the symlink should be created. |
| `group` | Category for organization and bulk actions. |
| `display_name` | (Optional) Human-readable name shown in menus. |
| `requires_sudo` | (Optional) Set to `true` for paths requiring root privileges. |

## Status Indicators

The interactive menu uses the following icons to represent the state of each configuration:

| Icon | Meaning |
|------|---------|
| `✓` (green) | Symlink exists and points correctly to the source. |
| `✗` (red) | Configuration is not linked to the system. |
| `⚠` (yellow) | **Conflict**: A file or directory exists at the target but is not a symlink. |
| `🔗` (cyan) | Symlink exists but points to an incorrect or outdated target. |
| `📁` (gray) | Source file or directory is missing in the `KONFIG_PATH`. |

## Workflows

### Bulk Operations
Navigate to **Browse** → **By Group** and select a group to perform actions like **Link All** or **Unlink All** on all configurations within that category.

### Conflict Resolution
If a conflict is detected (⚠), Konfig will prompt you with the following options:
1.  **Backup and Replace**: Moves the existing file/directory to `{target}.backup` and creates the symlink.
2.  **Skip**: Leaves the existing file untouched.
3.  **Abort**: Cancels the current operation.

## Troubleshooting

*   **"No clingy project found"**: Ensure you are executing the command within the directory initialized by `clingy init`.
*   **Permission Denied**: Verify that `requires_sudo: true` is set for configurations targeting system directories like `/etc/`.
*   **Missing Source**: Ensure the `source` path exists relative to the `KONFIG_PATH` defined in `config.py`.

---

## See Also

- [Clingy Documentation](../../README.md)
- [Architecture Overview](../../docs/architecture.md)
