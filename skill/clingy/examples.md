# clingy Complete Examples

This file contains complete, copy-pasteable examples of clingy commands.

---

## Example 1: Minimal Command

The simplest possible command with interactive menu support.

```python
"""Minimal command example"""

from argparse import ArgumentParser, Namespace

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_success
from clingy.core.menu import MenuNode


class HelloCommand(BaseCommand):
    """Simple hello world command"""

    name = "hello"
    help = "Say hello"
    description = "Minimal example command"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        pass  # No arguments needed

    def execute(self, args: Namespace) -> bool:
        """Execute hello command"""
        log_success("Hello, World!")
        return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu"""
        return MenuNode(
            label="Hello World",
            emoji=Emoji.GREET,
            action=lambda: self.execute(Namespace()),
        )
```

**Usage:**

```bash
# Interactive mode
clingy  # Select "Hello World"

# CLI mode
clingy hello
```

---

## Example 2: CRUD Command

Complete example with Create, Read, Update, Delete operations.

```python
"""CRUD command example - Manage items"""

import json
import os
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Optional

from config import DATA_DIR

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_error, log_info, log_section, log_success
from clingy.core.menu import MenuNode


class ItemsCommand(BaseCommand):
    """Manage items (CRUD operations)"""

    name = "items"
    help = "Manage items"
    description = "Create, read, update, and delete items"

    def __init__(self):
        super().__init__()
        self.items_file = os.path.join(DATA_DIR, "items.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _load_items(self) -> Dict[str, str]:
        """Load items from JSON file"""
        if not os.path.exists(self.items_file):
            return {}

        try:
            with open(self.items_file, "r") as f:
                return json.load(f)
        except Exception as e:
            log_error(f"Failed to load items: {e}")
            return {}

    def _save_items(self, items: Dict[str, str]) -> bool:
        """Save items to JSON file"""
        try:
            with open(self.items_file, "w") as f:
                json.dump(items, f, indent=2)
            return True
        except Exception as e:
            log_error(f"Failed to save items: {e}")
            return False

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        subparsers = parser.add_subparsers(dest="action", help="Action to perform")

        # Create
        create_parser = subparsers.add_parser("create", help="Create new item")
        create_parser.add_argument("name", help="Item name")
        create_parser.add_argument("value", help="Item value")

        # Read
        read_parser = subparsers.add_parser("read", help="Read item")
        read_parser.add_argument("name", nargs="?", help="Item name (optional)")

        # Update
        update_parser = subparsers.add_parser("update", help="Update item")
        update_parser.add_argument("name", help="Item name")
        update_parser.add_argument("value", help="New value")

        # Delete
        delete_parser = subparsers.add_parser("delete", help="Delete item")
        delete_parser.add_argument("name", help="Item name")

    def execute(self, args: Namespace) -> bool:
        """Execute CRUD operation"""
        action = getattr(args, "action", None)

        if action == "create":
            return self._create_item(args.name, args.value)
        elif action == "read":
            return self._read_items(getattr(args, "name", None))
        elif action == "update":
            return self._update_item(args.name, args.value)
        elif action == "delete":
            return self._delete_item(args.name)
        else:
            log_info("Use interactive menu or specify action: create, read, update, delete")
            return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for CRUD operations"""
        return MenuNode(
            label="Items",
            emoji=Emoji.LIST,
            children=[
                MenuNode(
                    label="List All Items",
                    emoji=Emoji.FILE_LIST,
                    action=lambda: self._read_items(None),
                ),
                MenuNode(
                    label="Create Item",
                    emoji=Emoji.FILE_CREATE,
                    action=lambda: self._create_item_interactive(),
                ),
                MenuNode(
                    label="Update Item",
                    emoji=Emoji.PENCIL,
                    action=lambda: self._update_item_interactive(),
                ),
                MenuNode(
                    label="Delete Item",
                    emoji=Emoji.FILE_DELETE,
                    action=lambda: self._delete_item_interactive(),
                ),
            ],
        )

    # ========================================================================
    # Create
    # ========================================================================

    def _create_item(self, name: str, value: str) -> bool:
        """Create new item"""
        items = self._load_items()

        if name in items:
            log_error(f"Item '{name}' already exists")
            return False

        items[name] = value

        if self._save_items(items):
            log_success(f"Created item: {name} = {value}")
            return True
        else:
            return False

    def _create_item_interactive(self) -> bool:
        """Create item with user input"""
        try:
            name = input("Enter item name: ").strip()
            if not name:
                log_error("Item name cannot be empty")
                return False

            value = input("Enter item value: ").strip()
            if not value:
                log_error("Item value cannot be empty")
                return False

            return self._create_item(name, value)
        except KeyboardInterrupt:
            log_info("Cancelled")
            return False

    # ========================================================================
    # Read
    # ========================================================================

    def _read_items(self, name: Optional[str] = None) -> bool:
        """Read items (all or specific)"""
        items = self._load_items()

        if not items:
            log_info("No items found")
            return True

        if name:
            # Read specific item
            if name not in items:
                log_error(f"Item '{name}' not found")
                return False

            log_section(f"ITEM: {name}")
            log_info(f"Value: {items[name]}")
        else:
            # Read all items
            log_section(f"ALL ITEMS ({len(items)})")
            for item_name, item_value in items.items():
                log_info(f"{item_name}: {item_value}")

        return True

    # ========================================================================
    # Update
    # ========================================================================

    def _update_item(self, name: str, value: str) -> bool:
        """Update existing item"""
        items = self._load_items()

        if name not in items:
            log_error(f"Item '{name}' not found")
            return False

        old_value = items[name]
        items[name] = value

        if self._save_items(items):
            log_success(f"Updated item: {name}")
            log_info(f"Old value: {old_value}")
            log_info(f"New value: {value}")
            return True
        else:
            return False

    def _update_item_interactive(self) -> bool:
        """Update item with user input"""
        items = self._load_items()

        if not items:
            log_info("No items to update")
            return False

        try:
            # Show available items
            log_section("AVAILABLE ITEMS")
            for item_name in items.keys():
                log_info(item_name)

            name = input("\nEnter item name to update: ").strip()
            if not name:
                log_error("Item name cannot be empty")
                return False

            if name not in items:
                log_error(f"Item '{name}' not found")
                return False

            log_info(f"Current value: {items[name]}")
            value = input("Enter new value: ").strip()
            if not value:
                log_error("Item value cannot be empty")
                return False

            return self._update_item(name, value)
        except KeyboardInterrupt:
            log_info("Cancelled")
            return False

    # ========================================================================
    # Delete
    # ========================================================================

    def _delete_item(self, name: str) -> bool:
        """Delete item"""
        items = self._load_items()

        if name not in items:
            log_error(f"Item '{name}' not found")
            return False

        del items[name]

        if self._save_items(items):
            log_success(f"Deleted item: {name}")
            return True
        else:
            return False

    def _delete_item_interactive(self) -> bool:
        """Delete item with user input"""
        items = self._load_items()

        if not items:
            log_info("No items to delete")
            return False

        try:
            # Show available items
            log_section("AVAILABLE ITEMS")
            for item_name in items.keys():
                log_info(item_name)

            name = input("\nEnter item name to delete: ").strip()
            if not name:
                log_error("Item name cannot be empty")
                return False

            # Confirm deletion
            confirm = input(f"Delete '{name}'? (y/N): ").strip().lower()
            if confirm != "y":
                log_info("Cancelled")
                return False

            return self._delete_item(name)
        except KeyboardInterrupt:
            log_info("Cancelled")
            return False
```

**Usage:**

```bash
# Interactive mode
clingy  # Select "Items" → "Create Item"

# CLI mode
clingy items create my-item "my value"
clingy items read
clingy items read my-item
clingy items update my-item "new value"
clingy items delete my-item
```

---

## Example 3: Build Pipeline Command

Complete example like the serverless template (build → zip → deploy).

```python
"""Build pipeline command - Build, Zip, Deploy"""

import os
import shutil
import subprocess
import zipfile
from argparse import ArgumentParser, Namespace
from typing import List

from config import GO_FUNCTIONS, OUTPUT_DIR

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_error, log_info, log_section, log_success
from clingy.core.menu import MenuNode, fzf_select_items
from clingy.core.stats import stats


class PipelineCommand(BaseCommand):
    """Build pipeline (Build → Zip → Deploy)"""

    name = "pipeline"
    help = "Build pipeline"
    description = "Build, zip, and deploy Go Lambda functions"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument("-f", "--function", help="Specific function to process")
        parser.add_argument("--skip-build", action="store_true", help="Skip build step")
        parser.add_argument("--skip-zip", action="store_true", help="Skip zip step")
        parser.add_argument("--skip-deploy", action="store_true", help="Skip deploy step")

    def execute(self, args: Namespace) -> bool:
        """Execute pipeline"""
        functions = [args.function] if args.function else GO_FUNCTIONS

        return self._run_pipeline(
            functions,
            skip_build=getattr(args, "skip_build", False),
            skip_zip=getattr(args, "skip_zip", False),
            skip_deploy=getattr(args, "skip_deploy", False),
        )

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for pipeline"""
        return MenuNode(
            label="Pipeline",
            emoji=Emoji.ROCKET,
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
                    label="Zip Functions",
                    emoji=Emoji.ZIP,
                    children=[
                        MenuNode(
                            label="Zip All",
                            action=lambda: self._zip_all(),
                        ),
                        MenuNode(
                            label="Select Functions to Zip",
                            action=lambda: self._zip_selected(),
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
                    label="Full Pipeline (Build → Zip → Deploy)",
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
                    action=lambda: self._clean_all(),
                ),
            ],
        )

    # ========================================================================
    # Build
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
        stats.reset()
        stats.total_items = len(functions)

        for func in functions:
            log_info(f"Building {func}...")

            # Build Go binary
            result = subprocess.run(
                [
                    "go",
                    "build",
                    "-o",
                    f"bin/{func}/bootstrap",
                    f"cmd/{func}/main.go",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                stats.add_success()
                log_success(f"{func} → built")
            else:
                stats.add_failure(func)
                log_error(f"{func} → build failed")
                log_error(result.stderr.strip())

        from clingy.core.logger import print_summary

        print_summary()
        return stats.success_count > 0

    # ========================================================================
    # Zip
    # ========================================================================

    def _zip_all(self) -> bool:
        """Zip all functions"""
        log_section("ZIP ALL FUNCTIONS")
        return self._zip_functions(GO_FUNCTIONS)

    def _zip_selected(self) -> bool:
        """Zip selected functions"""
        functions = fzf_select_items(
            items=GO_FUNCTIONS,
            prompt="Select functions to zip: ",
            include_all=False,
        )

        if not functions:
            log_info("No functions selected")
            return False

        log_section(f"ZIP {len(functions)} FUNCTIONS")
        return self._zip_functions(functions)

    def _zip_functions(self, functions: List[str]) -> bool:
        """Zip specified functions"""
        stats.reset()
        stats.total_items = len(functions)

        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for func in functions:
            log_info(f"Zipping {func}...")

            binary_path = f"bin/{func}/bootstrap"
            zip_path = os.path.join(OUTPUT_DIR, f"{func}.zip")

            # Check if binary exists
            if not os.path.exists(binary_path):
                stats.add_failure(func)
                log_error(f"{func} → binary not found (run build first)")
                continue

            try:
                # Create zip file
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(binary_path, "bootstrap")

                stats.add_success()
                log_success(f"{func} → zipped")
            except Exception as e:
                stats.add_failure(func)
                log_error(f"{func} → zip failed: {e}")

        from clingy.core.logger import print_summary

        print_summary()
        return stats.success_count > 0

    # ========================================================================
    # Deploy
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
        stats.reset()
        stats.total_items = len(functions)

        for func in functions:
            log_info(f"Deploying {func}...")

            zip_path = os.path.join(OUTPUT_DIR, f"{func}.zip")

            # Check if zip exists
            if not os.path.exists(zip_path):
                stats.add_failure(func)
                log_error(f"{func} → zip not found (run zip first)")
                continue

            # Deploy to AWS Lambda
            result = subprocess.run(
                [
                    "aws",
                    "lambda",
                    "update-function-code",
                    "--function-name",
                    func,
                    "--zip-file",
                    f"fileb://{zip_path}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                stats.add_success()
                log_success(f"{func} → deployed")
            else:
                stats.add_failure(func)
                log_error(f"{func} → deploy failed")
                log_error(result.stderr.strip())

        from clingy.core.logger import print_summary

        print_summary()
        return stats.success_count > 0

    # ========================================================================
    # Full Pipeline
    # ========================================================================

    def _full_pipeline_all(self) -> bool:
        """Run full pipeline for all functions"""
        log_section("FULL PIPELINE - ALL FUNCTIONS")
        return self._run_pipeline(GO_FUNCTIONS)

    def _full_pipeline_selected(self) -> bool:
        """Run full pipeline for selected functions"""
        functions = fzf_select_items(
            items=GO_FUNCTIONS,
            prompt="Select functions for full pipeline: ",
            include_all=False,
        )

        if not functions:
            log_info("No functions selected")
            return False

        log_section(f"FULL PIPELINE - {len(functions)} FUNCTIONS")
        return self._run_pipeline(functions)

    def _run_pipeline(
        self,
        functions: List[str],
        skip_build: bool = False,
        skip_zip: bool = False,
        skip_deploy: bool = False,
    ) -> bool:
        """Run full pipeline (Build → Zip → Deploy)"""
        # Build
        if not skip_build:
            log_info("Step 1/3: Building...")
            if not self._build_functions(functions):
                log_error("Build failed, aborting pipeline")
                return False

        # Zip
        if not skip_zip:
            log_info("Step 2/3: Zipping...")
            if not self._zip_functions(functions):
                log_error("Zip failed, aborting pipeline")
                return False

        # Deploy
        if not skip_deploy:
            log_info("Step 3/3: Deploying...")
            if not self._deploy_functions(functions):
                log_error("Deploy failed")
                return False

        log_success("Full pipeline completed successfully")
        return True

    # ========================================================================
    # Clean
    # ========================================================================

    def _clean_all(self) -> bool:
        """Clean all build artifacts"""
        log_section("CLEAN BUILD ARTIFACTS")

        # Clean bin directory
        if os.path.exists("bin"):
            shutil.rmtree("bin")
            log_success("Removed bin/")

        # Clean output directory
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
            log_success(f"Removed {OUTPUT_DIR}/")

        log_success("Clean completed")
        return True
```

**Usage:**

```bash
# Interactive mode
clingy  # Select "Pipeline" → "Full Pipeline - All Functions"

# CLI mode
clingy pipeline                          # Full pipeline (all functions)
clingy pipeline --function my-function   # Full pipeline (specific function)
clingy pipeline --skip-build             # Skip build step
```

---

## Example 4: Status Command

Complete example showing system information and checks.

```python
"""Status command - Show system and project status"""

import os
import platform
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Optional

from config import GO_FUNCTIONS, PROJECT_NAME, PROJECT_VERSION

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_error, log_info, log_section, log_success, log_warning
from clingy.core.menu import MenuNode


class StatusCommand(BaseCommand):
    """Show system and project status"""

    name = "status"
    help = "Show status"
    description = "Display system and project status information"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument("--verbose", action="store_true", help="Show verbose information")

    def execute(self, args: Namespace) -> bool:
        """Execute status command"""
        verbose = getattr(args, "verbose", False)

        self._show_project_info()
        self._show_system_info(verbose)
        self._show_dependencies()
        self._show_functions_status()

        return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for status command"""
        return MenuNode(
            label="Status",
            emoji=Emoji.INFO,
            children=[
                MenuNode(
                    label="Full Status",
                    emoji=Emoji.STATS,
                    action=lambda: self.execute(Namespace(verbose=False)),
                ),
                MenuNode(
                    label="Full Status (Verbose)",
                    emoji=Emoji.STATS,
                    action=lambda: self.execute(Namespace(verbose=True)),
                ),
                MenuNode(
                    label="Project Info",
                    emoji=Emoji.DOCUMENT,
                    action=lambda: self._show_project_info(),
                ),
                MenuNode(
                    label="System Info",
                    emoji=Emoji.COMPUTER,
                    action=lambda: self._show_system_info(verbose=False),
                ),
                MenuNode(
                    label="Dependencies",
                    emoji=Emoji.PACKAGE,
                    action=lambda: self._show_dependencies(),
                ),
                MenuNode(
                    label="Functions Status",
                    emoji=Emoji.LAMBDA,
                    action=lambda: self._show_functions_status(),
                ),
            ],
        )

    # ========================================================================
    # Status Sections
    # ========================================================================

    def _show_project_info(self) -> bool:
        """Show project information"""
        log_section("PROJECT INFORMATION")
        log_info(f"Name: {PROJECT_NAME}")
        log_info(f"Version: {PROJECT_VERSION}")
        log_info(f"Functions: {len(GO_FUNCTIONS)}")
        return True

    def _show_system_info(self, verbose: bool = False) -> bool:
        """Show system information"""
        log_section("SYSTEM INFORMATION")
        log_info(f"OS: {platform.system()} {platform.release()}")
        log_info(f"Python: {sys.version.split()[0]}")
        log_info(f"Platform: {platform.platform()}")

        if verbose:
            log_info(f"Machine: {platform.machine()}")
            log_info(f"Processor: {platform.processor()}")
            log_info(f"Architecture: {platform.architecture()[0]}")

        return True

    def _show_dependencies(self) -> bool:
        """Show dependencies status"""
        log_section("DEPENDENCIES")

        dependencies = {
            "go": ["go", "version"],
            "aws": ["aws", "--version"],
            "fzf": ["fzf", "--version"],
        }

        for name, command in dependencies.items():
            version = self._get_command_version(command)
            if version:
                log_success(f"{name}: {version}")
            else:
                log_error(f"{name}: not found")

        return True

    def _show_functions_status(self) -> bool:
        """Show functions build status"""
        log_section("FUNCTIONS STATUS")

        for func in GO_FUNCTIONS:
            binary_exists = os.path.exists(f"bin/{func}/bootstrap")
            zip_exists = os.path.exists(f"output/{func}.zip")

            status_parts = []
            if binary_exists:
                status_parts.append("built")
            if zip_exists:
                status_parts.append("zipped")

            if status_parts:
                status = ", ".join(status_parts)
                log_success(f"{func}: {status}")
            else:
                log_warning(f"{func}: not built")

        return True

    # ========================================================================
    # Helpers
    # ========================================================================

    def _get_command_version(self, command: list) -> Optional[str]:
        """Get version of a command"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=5
            )
            # Return first line of output
            output = result.stdout.strip() or result.stderr.strip()
            return output.split("\n")[0] if output else None
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None
```

**Usage:**

```bash
# Interactive mode
clingy  # Select "Status" → "Full Status"

# CLI mode
clingy status
clingy status --verbose
```

---

## Example 5: Interactive Calculator

Complete example with user input and operations.

```python
"""Calculator command - Interactive arithmetic operations"""

from argparse import ArgumentParser, Namespace

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_error, log_success
from clingy.core.menu import MenuNode


class CalculatorCommand(BaseCommand):
    """Simple calculator with interactive operation selection"""

    name = "calculator"
    help = "Simple calculator"
    description = "Perform basic arithmetic operations"

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument("num1", type=float, nargs="?", help="First number")
        parser.add_argument(
            "operation", nargs="?", choices=["+", "-", "*", "/"], help="Operation"
        )
        parser.add_argument("num2", type=float, nargs="?", help="Second number")

    def execute(self, args: Namespace) -> bool:
        """Execute calculation"""
        if not all([args.num1, args.operation, args.num2]):
            log_error("Missing arguments. Usage: calculator <num1> <operation> <num2>")
            return False

        return self._calculate(args.num1, args.operation, args.num2)

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu for calculator"""
        return MenuNode(
            label="Calculator",
            emoji=Emoji.CALCULATOR,
            children=[
                MenuNode(
                    label="Add",
                    emoji=Emoji.ADD,
                    action=lambda: self._calculate_interactive("+"),
                ),
                MenuNode(
                    label="Subtract",
                    emoji=Emoji.SUBTRACT,
                    action=lambda: self._calculate_interactive("-"),
                ),
                MenuNode(
                    label="Multiply",
                    emoji=Emoji.MULTIPLY,
                    action=lambda: self._calculate_interactive("*"),
                ),
                MenuNode(
                    label="Divide",
                    emoji=Emoji.DIVIDE,
                    action=lambda: self._calculate_interactive("/"),
                ),
            ],
        )

    def _calculate(self, num1: float, operation: str, num2: float) -> bool:
        """Perform calculation"""
        try:
            if operation == "+":
                result = num1 + num2
            elif operation == "-":
                result = num1 - num2
            elif operation == "*":
                result = num1 * num2
            elif operation == "/":
                if num2 == 0:
                    log_error("Division by zero")
                    return False
                result = num1 / num2
            else:
                log_error(f"Invalid operation: {operation}")
                return False

            log_success(f"{num1} {operation} {num2} = {result}")
            return True
        except Exception as e:
            log_error(f"Calculation failed: {e}")
            return False

    def _calculate_interactive(self, operation: str) -> bool:
        """Calculate with user input"""
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            return self._calculate(num1, operation, num2)
        except ValueError:
            log_error("Invalid number input")
            return False
        except KeyboardInterrupt:
            log_error("Cancelled")
            return False
```

**Usage:**

```bash
# Interactive mode
clingy  # Select "Calculator" → "Add"

# CLI mode
clingy calculator 10 + 5
clingy calculator 20 / 4
```

---

## Example 6: Dynamic Menu with Real-Time State

Example showing dynamic labels that update based on current state.

```python
"""Server command - Manage server with dynamic status"""

import subprocess
from argparse import ArgumentParser, Namespace
from typing import Optional

from clingy.commands.base import BaseCommand
from clingy.core.emojis import Emoji
from clingy.core.logger import log_error, log_info, log_success
from clingy.core.menu import MenuNode


class ServerCommand(BaseCommand):
    """Manage server with dynamic status display"""

    name = "server"
    help = "Manage server"
    description = "Start, stop, and check server status"

    def __init__(self):
        super().__init__()
        self.server_process: Optional[subprocess.Popen] = None

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments"""
        parser.add_argument(
            "action", nargs="?", choices=["start", "stop", "status"], help="Action"
        )

    def execute(self, args: Namespace) -> bool:
        """Execute server command"""
        action = getattr(args, "action", None)

        if action == "start":
            return self._start_server()
        elif action == "stop":
            return self._stop_server()
        elif action == "status":
            return self._show_status()
        else:
            log_info("Use interactive menu or specify action: start, stop, status")
            return True

    def get_menu_tree(self) -> MenuNode:
        """Interactive menu with dynamic status"""
        return MenuNode(
            label="Server",
            emoji=Emoji.SERVER_PLUS,
            children=[
                MenuNode(
                    label_generator=lambda: f"Status: {self._get_status_text()}",
                    emoji=Emoji.INFO,
                    action=lambda: self._show_status(),
                ),
                MenuNode(
                    label="Start Server",
                    emoji=Emoji.SERVER_PLUS,
                    action=lambda: self._start_server(),
                ),
                MenuNode(
                    label="Stop Server",
                    emoji=Emoji.SERVER_MINUS,
                    action=lambda: self._stop_server(),
                ),
            ],
        )

    # ========================================================================
    # Server Actions
    # ========================================================================

    def _start_server(self) -> bool:
        """Start server"""
        if self._is_running():
            log_error("Server is already running")
            return False

        log_info("Starting server...")

        try:
            # Start server process (example: Python HTTP server)
            self.server_process = subprocess.Popen(
                ["python", "-m", "http.server", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            log_success("Server started on http://localhost:8000")
            return True
        except Exception as e:
            log_error(f"Failed to start server: {e}")
            return False

    def _stop_server(self) -> bool:
        """Stop server"""
        if not self._is_running():
            log_error("Server is not running")
            return False

        log_info("Stopping server...")

        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.server_process = None

            log_success("Server stopped")
            return True
        except Exception as e:
            log_error(f"Failed to stop server: {e}")
            return False

    def _show_status(self) -> bool:
        """Show server status"""
        if self._is_running():
            log_success("Server is running on http://localhost:8000")
        else:
            log_info("Server is not running")
        return True

    # ========================================================================
    # Helpers
    # ========================================================================

    def _is_running(self) -> bool:
        """Check if server is running"""
        if self.server_process is None:
            return False

        # Check if process is still alive
        return self.server_process.poll() is None

    def _get_status_text(self) -> str:
        """Get status text for dynamic label"""
        return "Running" if self._is_running() else "Stopped"
```

**Usage:**

```bash
# Interactive mode
clingy  # Select "Server" → "Start Server"
# Menu shows: "Status: Running" (updates in real-time)

# CLI mode
clingy server start
clingy server status
clingy server stop
```

---

## Notes

- All examples are complete and ready to use
- Copy the code to `commands/` directory in your project
- Customize `config.py` with your project-specific settings
- Run `clingy` to test interactive mode
- Run `clingy <command>` to test CLI mode

**Last Updated:** 2026-03-27
