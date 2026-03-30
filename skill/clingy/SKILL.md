---
name: clingy
description: Context-aware CLI framework expert - Build interactive command-line tools with fzf menus, auto-discovery, and modular architecture
compatibility: Claude Code, OpenCode
metadata:
  author: ncasatti
  version: 1.1.0
  tags: python, cli, framework, fzf, interactive-menus, auto-discovery
---

# clingy Framework Skill

## Overview

**clingy** is a context-aware CLI framework for building interactive command-line tools with fuzzy search menus and modular command architecture. It works like Git/Poetry/Terraform - install once, use everywhere.

### Key Features

- **Interactive Menus**: fzf-powered fuzzy search navigation
- **Auto-Discovery**: Commands are automatically registered from `commands/` directory
- **Dual Mode**: Works in both CLI mode (`manager command --flag`) and interactive mode (`manager`)
- **Templates**: Pre-built templates (basic, serverless, konfig) for quick project setup
- **Context-Aware**: Automatically finds project root from any subdirectory
- **Modular Architecture**: Each command is a self-contained module

### When to Use This Skill

**Use this skill when:**
- ✅ Building CLI tools with interactive menus
- ✅ Creating clingy commands
- ✅ Working on clingy templates (serverless, konfig, basic)
- ✅ Implementing fzf-based selection menus
- ✅ Adding new features to clingy framework

**DON'T use this skill for:**
- ❌ General Python development (not manager-specific)
- ❌ Web frameworks (Flask, Django, FastAPI)
- ❌ Other CLI frameworks (Click, Typer, argparse)

---

## Quick Reference

### Common Commands

```bash
# Install framework (development mode)
uv pip install -e .

# Or with pip:
# pip install -e .

# Initialize new project
clingy init                              # basic template
clingy init --template serverless        # serverless template
clingy init --template konfig            # konfig template

# Interactive mode (recommended)
clingy                                   # Starts fuzzy-searchable menu

# CLI mode (traditional)
clingy <command> [options]
clingy greet --language es
clingy info

# Development
pytest tests/ -v                          # Run tests
black clingy/ tests/ --line-length 100  # Format code
isort clingy/ tests/ --profile black    # Sort imports
```

### Project Structure

```
my-project/
├── commands/           # Your commands here (auto-discovered)
│   ├── mycommand.py
│   └── __init__.py
├── config.py          # Configuration (ITEMS, PROJECT_NAME, etc.)
└── manager.py         # Entry point (optional)
```

### Essential Code Patterns

```python
# 1. Basic command structure
from clingy.commands.base import BaseCommand
from clingy.core.menu import MenuNode
from clingy.core.emojis import Emoji
from argparse import Namespace

class MyCommand(BaseCommand):
    name = "mycommand"
    help = "Short description"
    
    def add_arguments(self, parser):
        parser.add_argument('--option', help='Option description')
    
    def execute(self, args: Namespace) -> bool:
        # Your logic here
        return True
    
    def get_menu_tree(self) -> MenuNode:
        return MenuNode(
            label="My Command",
            emoji=Emoji.GEAR,
            action=lambda: self.execute(Namespace())
        )

# 2. Item selection with fzf
from clingy.core.menu import fzf_select_items
from config import ITEMS

items = fzf_select_items(
    items=ITEMS,
    prompt="Select items: ",
    include_all=True
)

# 3. Logging (NEVER use print)
from clingy.core.logger import log_success, log_error, log_info

log_info("Processing...")
log_success("Done!")
log_error("Failed!")
```

---

## Core Concepts

### 1. BaseCommand

All commands **must** inherit from `BaseCommand` and implement these methods:

```python
from clingy.commands.base import BaseCommand
from argparse import ArgumentParser, Namespace
from clingy.core.menu import MenuNode

class MyCommand(BaseCommand):
    # Class attributes
    name: str = "mycommand"           # CLI command name
    help: str = "Short help text"     # Shown in --help
    description: str = "Detailed..."  # Optional, defaults to help
    epilog: str = "Examples:\n..."    # Optional usage examples
    
    def add_arguments(self, parser: ArgumentParser):
        """Add command-specific CLI arguments"""
        parser.add_argument('--flag', help='Description')
    
    def execute(self, args: Namespace) -> bool:
        """
        Execute the command logic.
        
        Returns:
            True on success, False on failure
        """
        # Your implementation
        return True
    
    def get_menu_tree(self) -> MenuNode:
        """
        REQUIRED: Define interactive menu structure.
        
        All commands must implement this method (abstract).
        """
        return MenuNode(
            label="My Command",
            emoji=Emoji.GEAR,
            action=lambda: self.execute(Namespace())
        )
```

**Key Points:**
- `name`: Used for CLI invocation (`clingy mycommand`)
- `execute()`: Contains the actual command logic
- `get_menu_tree()`: **MANDATORY** - defines interactive menu structure
- Return `bool`: `True` for success, `False` for failure (affects exit code)

### 2. MenuNode

Tree structure for building interactive menus:

```python
from clingy.core.menu import MenuNode
from clingy.core.emojis import Emoji

# Leaf node (executable action)
MenuNode(
    label="Process All",
    emoji=Emoji.RUN,
    action=lambda: self._process_all()  # Function to execute
)

# Submenu node (navigable)
MenuNode(
    label="Functions",
    emoji=Emoji.LAMBDA,
    children=[
        MenuNode(label="Build", action=lambda: self._build()),
        MenuNode(label="Deploy", action=lambda: self._deploy()),
    ]
)

# Dynamic label (real-time state)
MenuNode(
    label_generator=lambda: f"Status: {self._get_status()}",
    action=lambda: self._show_status()
)
```

**MenuNode Structure:**

```python
@dataclass
class MenuNode:
    label: str = ""                              # Static label
    emoji: str = ""                              # Optional emoji prefix
    children: List[MenuNode] = []                # Submenu items
    action: Optional[Callable[[], bool]] = None  # Function to execute
    data: Dict[str, Any] = {}                    # Extra context data
    label_generator: Optional[Callable[[], str]] = None  # Dynamic label
    
    def is_leaf(self) -> bool:        # True if executable (no children)
    def is_submenu(self) -> bool:     # True if has children
    def display_label(self) -> str:   # Formatted label for fzf
```

**Navigation Rules:**
- **Leaf nodes**: Have `action`, no `children` → executable
- **Submenu nodes**: Have `children`, no `action` → navigable
- **Dynamic labels**: Use `label_generator` for real-time updates
- **Back navigation**: fzf automatically adds "← Back" option
- **Breadcrumb**: Shows current path (e.g., "Main → Functions → Build")

### 3. fzf_select_items()

Multi-select interface for choosing items:

```python
from clingy.core.menu import fzf_select_items
from config import ITEMS

# Basic usage
items = fzf_select_items(
    items=ITEMS,                    # List of items to select from
    prompt="Select items: ",        # Prompt text
    include_all=True                # Add "All" option
)

if not items:
    log_info("No items selected")
    return False

# Process selected items
for item in items:
    log_info(f"Processing {item}")
```

**Parameters:**
- `items`: List of strings to select from (defaults to `ITEMS` from config)
- `prompt`: Prompt text shown in fzf
- `include_all`: If `True`, adds "All" option at the top

**Returns:**
- `List[str]`: Selected items
- `None`: User cancelled (ESC)

**User Experience:**
- Use `TAB` to select multiple items
- Use `↑/↓` to navigate
- Use `ENTER` to confirm
- Use `ESC` to cancel

### 4. Auto-Discovery

Commands are automatically discovered from the `commands/` directory:

```
my-project/
├── commands/
│   ├── __init__.py       # Required (can be empty)
│   ├── greet.py          # Auto-discovered
│   ├── process.py        # Auto-discovered
│   └── deploy.py         # Auto-discovered
└── config.py
```

**How it works:**
1. Framework scans `commands/` directory
2. Imports all Python files
3. Finds classes inheriting from `BaseCommand`
4. Registers them automatically (no manual registration needed)

**Requirements:**
- File must be in `commands/` directory
- Class must inherit from `BaseCommand`
- Class must implement all abstract methods
- `__init__.py` must exist (can be empty)

### 5. Templates

Pre-built project templates for quick setup:

```bash
# Basic template (simple commands)
clingy init

# Serverless template (AWS Lambda functions)
clingy init --template serverless

# Konfig template (configuration management)
clingy init --template konfig
```

**Template Structure:**

```
clingy/templates/
├── basic/
│   ├── commands/
│   │   ├── greet.py
│   │   ├── calculator.py
│   │   └── info.py
│   └── config.py
│
├── serverless/
│   ├── commands/
│   │   ├── functions.py      # Build, Zip, Deploy
│   │   ├── logs_menu.py      # CloudWatch logs
│   │   └── status.py         # Function status
│   └── config.py
│
└── konfig/
    ├── commands/
    │   └── konfig_commands.py
    └── config.py
```

---

## Critical Rules (NON-NEGOTIABLE)

### 1. ALWAYS Implement get_menu_tree()

**WRONG:**
```python
class MyCommand(BaseCommand):
    name = "mycommand"
    help = "My command"
    
    def execute(self, args):
        return True
    
    # ❌ Missing get_menu_tree() - will fail!
```

**CORRECT:**
```python
class MyCommand(BaseCommand):
    name = "mycommand"
    help = "My command"
    
    def execute(self, args):
        return True
    
    def get_menu_tree(self) -> MenuNode:
        return MenuNode(
            label="My Command",
            emoji=Emoji.GEAR,
            action=lambda: self.execute(Namespace())
        )
```

**Why:** `get_menu_tree()` is an **abstract method** - all commands must implement it.

### 2. ALWAYS Use log_* Functions (NOT print)

**WRONG:**
```python
print("Processing...")           # ❌ Don't use print
print(f"Success: {result}")      # ❌ Don't use print
```

**CORRECT:**
```python
from clingy.core.logger import log_info, log_success, log_error

log_info("Processing...")
log_success(f"Completed: {result}")
log_error("Failed!")
```

**Why:** Logger functions provide:
- Consistent formatting
- Color coding
- Emoji icons
- Statistics tracking

### 3. ALWAYS Use MenuNode for Interactive Menus

**WRONG:**
```python
def get_menu_tree(self):
    return {                     # ❌ Don't use dict
        "label": "My Command",
        "action": self.execute
    }
```

**CORRECT:**
```python
def get_menu_tree(self) -> MenuNode:
    return MenuNode(
        label="My Command",
        emoji=Emoji.GEAR,
        action=lambda: self.execute(Namespace())
    )
```

**Why:** MenuNode provides type safety and proper fzf integration.

### 4. ALWAYS Inherit from BaseCommand

**WRONG:**
```python
class MyCommand:                 # ❌ Missing BaseCommand
    def run(self):
        pass
```

**CORRECT:**
```python
from clingy.commands.base import BaseCommand

class MyCommand(BaseCommand):
    name = "mycommand"
    help = "My command"
    
    def execute(self, args):
        return True
    
    def get_menu_tree(self):
        return MenuNode(...)
```

**Why:** BaseCommand provides:
- Auto-discovery
- Argument parsing
- Menu integration
- Consistent interface

### 5. NEVER Hardcode Values (Use config.py)

**WRONG:**
```python
ITEMS = ["item-1", "item-2"]     # ❌ Hardcoded in command
OUTPUT_DIR = "/tmp/output"       # ❌ Hardcoded path
```

**CORRECT:**
```python
from config import ITEMS, OUTPUT_DIR

# Use config values
for item in ITEMS:
    process_item(item, OUTPUT_DIR)
```

**Why:** Configuration should be centralized for easy modification.

---

## Menu Architecture

### Hierarchical Menu Structure

clingy uses a **tree-based menu system** with fzf for navigation:

```
Main Menu
├── Greet
│   ├── English
│   ├── Spanish
│   ├── French
│   └── German
├── Functions
│   ├── Build Functions
│   │   ├── Build All
│   │   └── Select Functions to Build
│   ├── Deploy Functions
│   │   ├── Deploy All
│   │   └── Select Functions to Deploy
│   └── Clean Build Artifacts
└── System Information
```

### Menu Node Types

**1. Leaf Node (Executable)**

```python
MenuNode(
    label="Build All",
    emoji=Emoji.BUILD,
    action=lambda: self._build_all()  # Function to execute
)
```

- Has `action` (function to execute)
- No `children`
- Executes when selected
- Returns to parent after execution

**2. Submenu Node (Navigable)**

```python
MenuNode(
    label="Functions",
    emoji=Emoji.LAMBDA,
    children=[
        MenuNode(label="Build", action=lambda: self._build()),
        MenuNode(label="Deploy", action=lambda: self._deploy()),
    ]
)
```

- Has `children` (submenu items)
- No `action`
- Shows submenu when selected
- Automatically adds "← Back" option

**3. Dynamic Label Node**

```python
MenuNode(
    label_generator=lambda: f"Status: {self._get_current_status()}",
    emoji=Emoji.INFO,
    action=lambda: self._show_status()
)
```

- Uses `label_generator` instead of static `label`
- Label is computed in real-time
- Useful for showing current state

### Navigation Flow

```
User runs: clingy
    ↓
Framework loads commands from commands/
    ↓
Builds menu tree from get_menu_tree() methods
    ↓
Shows main menu with fzf
    ↓
User selects "Functions"
    ↓
Shows submenu: Build, Deploy, Clean
    ↓
User selects "Build All"
    ↓
Executes action: self._build_all()
    ↓
Returns to submenu (Functions)
    ↓
User presses ESC
    ↓
Returns to main menu
    ↓
User presses ESC twice
    ↓
Exits
```

### Keyboard Shortcuts

- `↑/↓`: Navigate options
- `TAB`: Multi-select (in fzf_select_items)
- `ENTER`: Confirm selection
- `ESC`: Go back (or exit if at root)
- `Ctrl+C`: Force exit

---

## Code Examples

### Example 1: Simple Command with Menu

```python
from argparse import ArgumentParser, Namespace

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_success
from clingy.core.menu import MenuNode


class GreetCommand(BaseCommand):
    """Greet users in different languages"""

    name = "greet"
    help = "Greet the user"
    description = "Simple greeting command with language selection"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument(
            "-l",
            "--language",
            choices=["en", "es", "fr", "de"],
            help="Language for greeting",
        )

    def execute(self, args: Namespace) -> bool:
        """Execute greeting"""
        greetings = {
            "en": "Hello, World!",
            "es": "¡Hola, Mundo!",
            "fr": "Bonjour, le monde!",
            "de": "Guten Tag, Welt!",
        }

        lang = getattr(args, "language", "en") or "en"
        log_success(greetings[lang])
        return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for greet command"""
        return MenuNode(
            label="Greet",
            emoji=Emoji.GREET,
            children=[
                MenuNode(
                    label="English",
                    emoji=Emoji.FLAG_GB,
                    action=lambda: self._greet("en"),
                ),
                MenuNode(
                    label="Spanish",
                    emoji=Emoji.FLAG_ES,
                    action=lambda: self._greet("es"),
                ),
                MenuNode(
                    label="French",
                    emoji=Emoji.FLAG_FR,
                    action=lambda: self._greet("fr"),
                ),
                MenuNode(
                    label="German",
                    emoji=Emoji.FLAG_DE,
                    action=lambda: self._greet("de"),
                ),
            ],
        )

    def _greet(self, language: str) -> bool:
        """Internal greeting method"""
        greetings = {
            "en": "Hello, World!",
            "es": "¡Hola, Mundo!",
            "fr": "Bonjour, le monde!",
            "de": "Guten Tag, Welt!",
        }
        log_success(greetings[language])
        return True
```

### Example 2: Command with Item Selection

```python
from argparse import ArgumentParser, Namespace
from typing import List

from config import ITEMS

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_info, log_section, log_success
from clingy.core.menu import MenuNode, fzf_select_items


class ProcessCommand(BaseCommand):
    """Process items with selection menu"""

    name = "process"
    help = "Process items"
    description = "Process items with interactive selection"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument("-i", "--item", help="Specific item to process")

    def execute(self, args: Namespace) -> bool:
        """Execute processing"""
        # Support both CLI and interactive mode
        if hasattr(args, "item") and args.item:
            items = [args.item]
        else:
            items = ITEMS

        return self._process_items(items)

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for process command"""
        return MenuNode(
            label="Process Items",
            emoji=Emoji.RUN,
            children=[
                MenuNode(
                    label="Process All",
                    emoji=Emoji.ALL,
                    action=lambda: self._process_all(),
                ),
                MenuNode(
                    label="Select Items",
                    emoji=Emoji.SEARCH,
                    action=lambda: self._process_selected(),
                ),
            ],
        )

    def _process_all(self) -> bool:
        """Process all items"""
        log_section("PROCESS ALL ITEMS")
        return self._process_items(ITEMS)

    def _process_selected(self) -> bool:
        """Let user select items to process"""
        items = fzf_select_items(
            items=ITEMS, prompt="Select items to process: ", include_all=False
        )

        if not items:
            log_info("No items selected")
            return False

        log_section(f"PROCESS {len(items)} ITEMS")
        return self._process_items(items)

    def _process_items(self, items: List[str]) -> bool:
        """Process specified items"""
        for item in items:
            log_info(f"Processing {item}...")
            # Your processing logic here
            log_success(f"{item} → completed")

        return True
```

### Example 3: Hierarchical Menu (3 Levels)

```python
from argparse import ArgumentParser, Namespace
from typing import List

from config import GO_FUNCTIONS

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_error, log_info, log_section, log_success
from clingy.core.menu import MenuNode, fzf_select_items


class FunctionsCommand(BaseCommand):
    """Manage Lambda functions (Build, Deploy, Clean)"""

    name = "functions"
    help = "Manage Lambda functions"
    description = "Build, deploy, and clean Go Lambda functions"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        pass

    def execute(self, args: Namespace) -> bool:
        """Execute functions command (not used in interactive mode)"""
        log_info("Use interactive menu to manage functions")
        return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for functions management"""
        return MenuNode(
            label="Functions",
            emoji=Emoji.LAMBDA,
            children=[
                MenuNode(
                    label="Build Functions",
                    emoji=Emoji.BUILD,
                    children=[
                        MenuNode(
                            label="Build All",
                            action=lambda: self._build_all(),
                        ),
                        MenuNode(
                            label="Select Functions to Build",
                            action=lambda: self._build_selected(),
                        ),
                    ],
                ),
                MenuNode(
                    label="Deploy Functions",
                    emoji=Emoji.DEPLOY,
                    children=[
                        MenuNode(
                            label="Deploy All",
                            action=lambda: self._deploy_all(),
                        ),
                        MenuNode(
                            label="Select Functions to Deploy",
                            action=lambda: self._deploy_selected(),
                        ),
                    ],
                ),
                MenuNode(
                    label="Full Pipeline (Build → Deploy)",
                    emoji=Emoji.ALL,
                    children=[
                        MenuNode(
                            label="Full Pipeline - All Functions",
                            action=lambda: self._full_pipeline_all(),
                        ),
                        MenuNode(
                            label="Full Pipeline - Select Functions",
                            action=lambda: self._full_pipeline_selected(),
                        ),
                    ],
                ),
                MenuNode(
                    label="Clean Build Artifacts",
                    emoji=Emoji.TRASH,
                    children=[
                        MenuNode(
                            label="Clean All",
                            action=lambda: self._clean_all(),
                        ),
                        MenuNode(
                            label="Select Functions to Clean",
                            action=lambda: self._clean_selected(),
                        ),
                    ],
                ),
            ],
        )

    # ========================================================================
    # Build Actions
    # ========================================================================

    def _build_all(self) -> bool:
        """Build all functions"""
        log_section("BUILD ALL FUNCTIONS")
        return self._build_functions(GO_FUNCTIONS)

    def _build_selected(self) -> bool:
        """Build selected functions"""
        functions = fzf_select_items(
            items=GO_FUNCTIONS,
            prompt="Select functions to build: ",
            include_all=False,
        )

        if not functions:
            log_info("No functions selected")
            return False

        log_section(f"BUILD {len(functions)} FUNCTIONS")
        return self._build_functions(functions)

    def _build_functions(self, functions: List[str]) -> bool:
        """Build specified functions"""
        for func in functions:
            log_info(f"Building {func}...")
            # Your build logic here
            log_success(f"{func} → built")
        return True

    # ========================================================================
    # Deploy Actions
    # ========================================================================

    def _deploy_all(self) -> bool:
        """Deploy all functions"""
        log_section("DEPLOY ALL FUNCTIONS")
        return self._deploy_functions(GO_FUNCTIONS)

    def _deploy_selected(self) -> bool:
        """Deploy selected functions"""
        functions = fzf_select_items(
            items=GO_FUNCTIONS,
            prompt="Select functions to deploy: ",
            include_all=False,
        )

        if not functions:
            log_info("No functions selected")
            return False

        log_section(f"DEPLOY {len(functions)} FUNCTIONS")
        return self._deploy_functions(functions)

    def _deploy_functions(self, functions: List[str]) -> bool:
        """Deploy specified functions"""
        for func in functions:
            log_info(f"Deploying {func}...")
            # Your deploy logic here
            log_success(f"{func} → deployed")
        return True

    # ========================================================================
    # Full Pipeline Actions
    # ========================================================================

    def _full_pipeline_all(self) -> bool:
        """Run full pipeline (Build → Deploy) for all functions"""
        log_section("FULL PIPELINE - ALL FUNCTIONS")

        # Build
        log_info("Step 1/2: Building...")
        if not self._build_functions(GO_FUNCTIONS):
            log_error("Build failed, aborting pipeline")
            return False

        # Deploy
        log_info("Step 2/2: Deploying...")
        if not self._deploy_functions(GO_FUNCTIONS):
            log_error("Deploy failed")
            return False

        log_success("Full pipeline completed successfully")
        return True

    def _full_pipeline_selected(self) -> bool:
        """Run full pipeline (Build → Deploy) for selected functions"""
        functions = fzf_select_items(
            items=GO_FUNCTIONS,
            prompt="Select functions for full pipeline: ",
            include_all=False,
        )

        if not functions:
            log_info("No functions selected")
            return False

        log_section(f"FULL PIPELINE - {len(functions)} FUNCTIONS")

        success = True
        for func in functions:
            log_info(f"Processing {func}...")

            # Build
            if not self._build_functions([func]):
                log_error(f"Build failed for {func}, skipping")
                success = False
                continue

            # Deploy
            if not self._deploy_functions([func]):
                log_error(f"Deploy failed for {func}")
                success = False

        if success:
            log_success("Full pipeline completed successfully")
        return success

    # ========================================================================
    # Clean Actions
    # ========================================================================

    def _clean_all(self) -> bool:
        """Clean all build artifacts"""
        log_section("CLEAN ALL BUILD ARTIFACTS")
        for func in GO_FUNCTIONS:
            log_info(f"Cleaning {func}...")
            # Your clean logic here
            log_success(f"{func} → cleaned")
        return True

    def _clean_selected(self) -> bool:
        """Clean selected functions"""
        functions = fzf_select_items(
            items=GO_FUNCTIONS,
            prompt="Select functions to clean: ",
            include_all=False,
        )

        if not functions:
            log_info("No functions selected")
            return False

        log_section(f"CLEAN {len(functions)} FUNCTIONS")
        for func in functions:
            log_info(f"Cleaning {func}...")
            # Your clean logic here
            log_success(f"{func} → cleaned")
        return True
```

---

## Common Patterns

### Pattern 1: CLI + Interactive Mode (Dual Support)

Support both CLI arguments and interactive menu selection:

```python
def execute(self, args: Namespace) -> bool:
    """Execute command (works for both CLI and interactive mode)"""
    # Check if specific item was provided via CLI
    if hasattr(args, "item") and args.item:
        items = [args.item]
    # Check if items were provided via interactive menu
    elif hasattr(args, "item_list") and args.item_list:
        items = args.item_list
    # Default to all items
    else:
        items = ITEMS
    
    if not items:
        log_error("No items to process")
        return False
    
    return self._process_items(items)
```

**Why:** This pattern allows the same command to work in both modes:
- CLI: `manager process --item item-1`
- Interactive: User selects from menu

### Pattern 2: Dynamic Labels (Real-time State)

Show current state in menu labels:

```python
def get_menu_tree(self) -> MenuNode:
    return MenuNode(
        label="Status",
        emoji=Emoji.INFO,
        children=[
            MenuNode(
                label_generator=lambda: f"Server: {self._get_server_status()}",
                action=lambda: self._show_server_status()
            ),
            MenuNode(
                label_generator=lambda: f"Database: {self._get_db_status()}",
                action=lambda: self._show_db_status()
            ),
        ]
    )

def _get_server_status(self) -> str:
    """Get current server status"""
    # Check server status
    return "Running" if server_is_running() else "Stopped"

def _get_db_status(self) -> str:
    """Get current database status"""
    # Check database status
    return "Connected" if db_is_connected() else "Disconnected"
```

**Why:** Labels are computed in real-time, showing current state.

### Pattern 3: Processing with Stats

Track and display statistics during processing:

```python
from clingy.core.stats import stats
from clingy.core.logger import print_summary

def _process_items(self, items: List[str]) -> bool:
    """Process items with statistics tracking"""
    # Reset stats
    stats.reset()
    stats.total_items = len(items)
    
    # Process items
    for item in items:
        log_info(f"Processing {item}...")
        
        try:
            # Your processing logic
            result = process_item(item)
            
            if result:
                stats.add_success()
                log_success(f"{item} → completed")
            else:
                stats.add_failure(item)
                log_error(f"{item} → failed")
        except Exception as e:
            stats.add_failure(item)
            log_error(f"{item} → error: {e}")
    
    # Print summary
    print_summary()
    
    return stats.success_count > 0
```

**Output:**
```
Processing item-1...
✅ item-1 → completed
Processing item-2...
❌ item-2 → failed
Processing item-3...
✅ item-3 → completed

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:    3
Success:  2
Failed:   1
```

### Pattern 4: Subprocess Execution

Execute external commands safely:

```python
import subprocess
from clingy.core.logger import log_error, log_info

def _build_function(self, function_name: str) -> bool:
    """Build Go Lambda function"""
    log_info(f"Building {function_name}...")
    
    try:
        result = subprocess.run(
            ["go", "build", "-o", f"bin/{function_name}", f"cmd/{function_name}/main.go"],
            check=True,           # Raise on error
            capture_output=True,  # Capture stdout/stderr
            text=True,            # Return strings (not bytes)
            cwd=".",              # Working directory
        )
        
        log_success(f"{function_name} → built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        log_error(f"Build failed: {e.stderr.strip()}")
        return False
        
    except FileNotFoundError:
        log_error("Go compiler not found. Install with: brew install go")
        return False
```

**Why:** Proper error handling and user-friendly error messages.

### Pattern 5: Validation and Error Handling

Validate inputs before processing:

```python
from config import ITEMS
from clingy.core.logger import log_error, log_info

def _process_item(self, item_name: str) -> bool:
    """Process a single item with validation"""
    # Validate item exists
    if item_name not in ITEMS:
        log_error(f"Item '{item_name}' not found")
        log_info(f"Available items: {', '.join(ITEMS[:5])}...")
        return False
    
    # Validate prerequisites
    if not self._check_prerequisites():
        log_error("Prerequisites not met")
        log_info("Run: pip install -r requirements.txt")
        return False
    
    # Process item
    try:
        # Your processing logic
        result = do_processing(item_name)
        
        if result:
            log_success(f"{item_name} → completed")
            return True
        else:
            log_error(f"{item_name} → failed")
            return False
            
    except Exception as e:
        log_error(f"{item_name} → error: {e}")
        return False

def _check_prerequisites(self) -> bool:
    """Check if prerequisites are met"""
    # Check dependencies, files, etc.
    return True
```

---

## Available Emojis

All emojis are defined in `clingy.core.emojis.Emoji`:

```python
from clingy.core.emojis import Emoji

# Status Indicators
Emoji.SUCCESS     # ✅ Success
Emoji.ERROR       # ❌ Error
Emoji.WARNING     # ⚠️ Warning
Emoji.INFO        # 󰋽 Information

# Actions
Emoji.ROCKET      # 🚀 Rocket
Emoji.BUILD       # 󱌣 Build
Emoji.CLEAN       # 🧹 Clean
Emoji.RUN         # ▶️ Run
Emoji.SEARCH      # 🔍 Search
Emoji.BACK        # 󰈆 Back
Emoji.EXIT        # 󰈆 Exit
Emoji.ZIP         # 📦 Zip
Emoji.DEPLOY      # 🚀 Deploy
Emoji.INVOKE      # 󰱑 Invoke

# Objects
Emoji.PACKAGE     # 📦 Package
Emoji.DOCUMENT    # 󱔗 Document
Emoji.LIST        # 📋 List
Emoji.FLOPPY      # 💾 Floppy
Emoji.COMPUTER    # 💻 Computer
Emoji.CLOUD       # ☁️ Cloud
Emoji.GEAR        # ⚙️ Gear
Emoji.LAMBDA      # 󰘧 Lambda
Emoji.ALL         # 󰁌 All

# Time & Stats
Emoji.TIME        # ⏱️ Time
Emoji.STATS       # 📊 Stats
Emoji.CIRCULAR    # 🔄 Circular
Emoji.BOLT        # ⚡ Bolt

# Server/Monitor
Emoji.SERVER_PLUS  # 󰒐 Server Plus
Emoji.SERVER_MINUS # 󰒌 Server Minus
Emoji.MONITOR      # 󰍹 Monitor
Emoji.MONITOR_IN   # 󱒃 Monitor In

# Edit Operations
Emoji.PENCIL       # 󰏫 Pencil
Emoji.PLUS         # ➕ Plus
Emoji.TRASH        # 🗑️ Trash
Emoji.QUICK_ACTIONS # 󰱑 Quick Actions

# Commands - Main Menu Icons
Emoji.FILES        # 📁 Files
Emoji.CALCULATOR   # 🧮 Calculator
Emoji.GREET        # 󰙊 Greet
Emoji.REQUIREMENTS # 📋 Requirements
Emoji.LOG          # 📜 Log
Emoji.LOG_REALTIME # 󱫒 Log Realtime

# Math Operations
Emoji.ADD          # ➕ Add
Emoji.SUBTRACT     # ➖ Subtract
Emoji.MULTIPLY     # ✖️ Multiply
Emoji.DIVIDE       # ➗ Divide

# File Operations
Emoji.FILE_LIST    # 📋 File List
Emoji.FILE_CREATE  # 󰻭 File Create
Emoji.FILE_DELETE  # 🗑️ File Delete
Emoji.LINK         # 🔗 Link
Emoji.UNLINK       # 󰌸 Unlink

# Languages/Flags
Emoji.FLAG_GB      # 🇬🇧 Great Britain
Emoji.FLAG_ES      # 🇪🇸 Spain
Emoji.FLAG_FR      # 🇫🇷 France
Emoji.FLAG_DE      # 🇩🇪 Germany
Emoji.FLAG_BR      # 🇧🇷 Brazil
Emoji.FLAG_IT      # 🇮🇹 Italy
```

**Usage:**

```python
from clingy.core.emojis import Emoji

MenuNode(
    label="Build",
    emoji=Emoji.BUILD,
    action=lambda: self._build()
)
```

---

## Project Initialization

### Step 1: Initialize Project

```bash
# Create project directory
mkdir my-cli-tool
cd my-cli-tool

# Initialize with template
clingy init                              # basic template
clingy init --template serverless        # serverless template
clingy init --template konfig            # konfig template
clingy init --force                      # overwrite existing
```

### Step 2: Customize Configuration

Edit `config.py`:

```python
# Project metadata
PROJECT_NAME = "My CLI Tool"
PROJECT_VERSION = "1.0.0"

# Items (customize based on your use case)
ITEMS = [
    "item-1",
    "item-2",
    "item-3",
]

# Directories
DATA_DIR = "data"
OUTPUT_DIR = "output"

# Add your custom configuration
MY_CUSTOM_SETTING = "value"
```

### Step 3: Create Your Commands

Create new files in `commands/`:

```python
# commands/mycommand.py
from argparse import ArgumentParser, Namespace

from config import ITEMS

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_success
from clingy.core.menu import MenuNode


class MyCommand(BaseCommand):
    """My custom command"""

    name = "mycommand"
    help = "My custom command"
    description = "Detailed description of my command"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument("--option", help="Option description")

    def execute(self, args: Namespace) -> bool:
        """Execute command logic"""
        for item in ITEMS:
            log_success(f"Processing {item}")
        return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu"""
        return MenuNode(
            label="My Command",
            emoji=Emoji.GEAR,
            children=[
                MenuNode(
                    label="Process All",
                    action=lambda: self.execute(Namespace()),
                ),
            ],
        )
```

### Step 4: Test

```bash
# Interactive mode
clingy

# CLI mode
clingy mycommand --option value

# Run from subdirectory (context-aware)
cd subdir
clingy  # Automatically finds project root
```

### Step 5: Update Documentation

Update `README.md` with your project details:

```markdown
# My CLI Tool

Description of your tool.

## Installation

```bash
uv pip install -e .
```

## Usage

```bash
# Interactive mode
clingy

# CLI mode
clingy mycommand --option value
```

## Commands

- `mycommand`: Description
- `another`: Description
```

---

## Development Workflow

### Running the CLI

```bash
# Install framework (development mode)
uv pip install -e .

# Or with pip:
# pip install -e .

# Interactive mode (recommended)
clingy                              # Starts fuzzy-searchable menu

# CLI mode (traditional)
clingy <command> [options]
clingy greet --language es
clingy info

# Run from any subdirectory (context-aware)
cd my-project/subdir
clingy  # Automatically finds project root
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_commands.py

# Run single test
pytest tests/test_mycommand.py::test_name

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb
```

### Linting/Formatting

**REQUIRED before commit:**

```bash
# Format code
black clingy/ tests/ --line-length 100
isort clingy/ tests/ --profile black

# Check without modifying (CI checks)
black clingy/ tests/ --check --line-length 100
isort clingy/ tests/ --check-only --profile black
```

**Optional (not configured):**

```bash
# Flake8 (style guide)
flake8 . --max-line-length=100

# MyPy (type checking)
mypy . --strict
```

### Pre-Commit Checks

**IMPORTANT:** Before committing, run these commands to ensure CI will pass:

```bash
# Run ALL CI checks locally (same as GitHub Actions)
black clingy/ tests/ --check --line-length 100
isort clingy/ tests/ --check-only --profile black

# If checks fail, format the code:
black clingy/ tests/ --line-length 100
isort clingy/ tests/ --profile black

# Then verify tests still pass:
pytest tests/ -v
```

**Why this matters:**
- GitHub Actions will fail if code is not formatted correctly
- Running checks locally saves CI time and prevents failed builds
- These are the EXACT commands that run in `.github/workflows/lint.yml`

---

## Troubleshooting

### Problem: "get_menu_tree() not implemented"

**Error:**
```
TypeError: Can't instantiate abstract class MyCommand with abstract method get_menu_tree
```

**Solution:**
All commands MUST implement `get_menu_tree()` (abstract method):

```python
def get_menu_tree(self) -> MenuNode:
    return MenuNode(
        label="My Command",
        emoji=Emoji.GEAR,
        action=lambda: self.execute(Namespace())
    )
```

### Problem: Menu doesn't show my command

**Symptoms:**
- Command file exists in `commands/`
- Command works in CLI mode
- Command doesn't appear in interactive menu

**Solution:**
Commands are auto-discovered from `commands/` directory. Check:

1. File is in correct location: `commands/mycommand.py`
2. `__init__.py` exists in `commands/` directory
3. Class inherits from `BaseCommand`
4. `get_menu_tree()` is implemented
5. No syntax errors in file

### Problem: fzf not found

**Error:**
```
fzf not found. Install it with: brew install fzf (macOS) or sudo apt install fzf (Linux)
```

**Solution:**

```bash
# macOS
brew install fzf

# Linux (Debian/Ubuntu)
sudo apt install fzf

# Linux (Fedora)
sudo dnf install fzf

# Verify installation
fzf --version
```

### Problem: Import errors

**Error:**
```
ModuleNotFoundError: No module named 'clingy'
```

**Solution:**

```bash
# Install framework in development mode
uv pip install -e .

# Or with pip:
# pip install -e .

# Verify installation
python -c "import clingy; print(clingy.__file__)"
```

### Problem: Command not auto-discovered

**Symptoms:**
- Command file exists
- No errors
- Command doesn't appear in `clingy --help`

**Solution:**

1. Check file location: Must be in `commands/` directory
2. Check class name: Must inherit from `BaseCommand`
3. Check `name` attribute: Must be set
4. Restart Python (clear import cache)

```python
# CORRECT
class MyCommand(BaseCommand):
    name = "mycommand"  # Required
    help = "My command"  # Required
    
    def execute(self, args):
        return True
    
    def get_menu_tree(self):
        return MenuNode(...)
```

### Problem: Menu navigation doesn't work

**Symptoms:**
- Menu shows but can't navigate
- ESC doesn't go back
- Selection doesn't work

**Solution:**

1. Check fzf is installed: `fzf --version`
2. Check MenuNode structure:
   - Leaf nodes have `action`, no `children`
   - Submenu nodes have `children`, no `action`
3. Check action returns `bool`:

```python
# CORRECT
MenuNode(
    label="Build",
    action=lambda: self._build()  # Must return bool
)

def _build(self) -> bool:
    # Your logic
    return True  # Must return bool
```

---

## Reference Documentation

For more details, see:

- **AGENTS.md** - Complete development guide for AI agents
- **CONTRIBUTING.md** - Contribution guidelines
- **README.md** - User documentation
- **examples.md** - Complete working examples

---

## Best Practices

### 1. Read Before Writing

If modifying a command, read similar commands first to understand patterns:

```bash
# Read existing commands
bat clingy/templates/basic/commands/greet.py
bat clingy/templates/serverless/commands/functions.py
```

### 2. Validate Inputs

Always validate inputs before processing:

```python
# Check item exists
if item_name not in ITEMS:
    log_error(f"Item '{item_name}' not found")
    log_info(f"Available: {', '.join(ITEMS)}")
    return False

# Check file exists
if not os.path.exists(file_path):
    log_error(f"File not found: {file_path}")
    return False
```

### 3. Atomic Operations

Each command should do ONE thing well:

```python
# GOOD: Single responsibility
class BuildCommand(BaseCommand):
    """Build Lambda functions"""
    def execute(self, args):
        return self._build_functions(args.functions)

# BAD: Multiple responsibilities
class BuildAndDeployCommand(BaseCommand):
    """Build and deploy Lambda functions"""
    def execute(self, args):
        self._build_functions(args.functions)
        self._deploy_functions(args.functions)  # Should be separate command
```

### 4. Interactive Support

Commands should work in both CLI and interactive menu:

```python
def execute(self, args: Namespace) -> bool:
    # Support CLI arguments
    if hasattr(args, "item") and args.item:
        items = [args.item]
    # Support interactive menu
    elif hasattr(args, "item_list") and args.item_list:
        items = args.item_list
    # Default to all items
    else:
        items = ITEMS
    
    return self._process_items(items)
```

### 5. Cross-Platform

Use `os.path.join()`, not hardcoded slashes:

```python
# GOOD: Cross-platform
output_path = os.path.join(OUTPUT_DIR, "file.txt")

# BAD: Unix-only
output_path = f"{OUTPUT_DIR}/file.txt"
```

### 6. Progress Feedback

Log each step (especially in long operations):

```python
def _build_functions(self, functions: List[str]) -> bool:
    log_section(f"BUILD {len(functions)} FUNCTIONS")
    
    for i, func in enumerate(functions, 1):
        log_info(f"[{i}/{len(functions)}] Building {func}...")
        
        if self._build_function(func):
            log_success(f"{func} → built")
        else:
            log_error(f"{func} → failed")
    
    return True
```

### 7. Clean State

Don't leave artifacts on failure:

```python
def _build_function(self, function_name: str) -> bool:
    temp_dir = f"/tmp/{function_name}"
    
    try:
        # Create temp directory
        os.makedirs(temp_dir, exist_ok=True)
        
        # Build
        result = subprocess.run(["go", "build", ...])
        
        if result.returncode != 0:
            # Clean up on failure
            shutil.rmtree(temp_dir)
            return False
        
        return True
        
    except Exception as e:
        # Clean up on exception
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        log_error(f"Build failed: {e}")
        return False
```

### 8. Documentation

Update README.md when adding new features:

```markdown
## Commands

### mycommand

Description of the command.

**Usage:**

```bash
# Interactive mode
clingy  # Select "My Command" from menu

# CLI mode
clingy mycommand --option value
```

**Options:**

- `--option`: Description of option
```

---

## Notes for AI Agents

- **No tests exist yet:** When writing tests, use pytest with fixtures
- **Auto-discovery:** New commands are auto-registered (no imports needed)
- **Base class helpers:** Use `_resolve_item_list()` and `_get_filtered_items()`
- **Interactive menus:** Implement `get_menu_tree()` to add interactive support (MANDATORY)
- **Menu system:** Uses `MenuNode` (tree structure) + `MenuRenderer` (fzf navigation)
- **Item selection:** Use `fzf_select_items()` for multi-select in menus
- **Colors/Emojis:** Already handled by logger utilities
- **Configuration:** All settings in `config.py` (never hardcode values)
- **Items:** Defined in `config.py:ITEMS` (not tied to any specific resource type)
- **Linting:** Use black with line-length 100
- **Comments:** All comments must be in English
- **get_menu_tree():** Now mandatory (abstract method), not optional
- **Emojis:** Centralized in `core/emojis.py` `Emoji` class

---

**Last Updated:** 2026-03-27  
**Python Version:** 3.8+  
**Framework Version:** 1.1.0  
**Primary Maintainer:** @ncasatti
