# Manager-Core Skill

Expert skill for building interactive CLI tools with the manager-core framework.

## Files

- **SKILL.md** - Main skill file with comprehensive documentation
- **examples.md** - Complete, copy-pasteable code examples

## Usage

Load this skill when working with manager-core projects:

```bash
# In OpenCode
@skill manager-core
```

## What This Skill Teaches

- Building interactive menus with fzf
- Creating auto-discovered commands
- Implementing MenuNode tree structures
- Using fzf_select_items for multi-select
- Proper logging and error handling
- Project initialization and templates
- Best practices and common patterns

## Quick Reference

### Minimal Command

```python
from manager_core.commands.base import BaseCommand
from manager_core.core.menu import MenuNode
from manager_core.core.emojis import Emoji

class MyCommand(BaseCommand):
    name = "mycommand"
    help = "My command"
    
    def execute(self, args):
        return True
    
    def get_menu_tree(self):
        return MenuNode(
            label="My Command",
            emoji=Emoji.GEAR,
            action=lambda: self.execute(Namespace())
        )
```

### Interactive Menu

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

### Item Selection

```python
from manager_core.core.menu import fzf_select_items

items = fzf_select_items(
    items=ITEMS,
    prompt="Select items: ",
    include_all=True
)
```

## When to Use

✅ Building CLI tools with interactive menus  
✅ Creating manager-core commands  
✅ Working on manager-core templates  
✅ Implementing fzf-based selection menus  

❌ General Python development  
❌ Web frameworks  
❌ Other CLI frameworks  

---

**Version:** 1.0.0  
**Author:** @ncasatti  
**Last Updated:** 2026-01-29
