---
name: conversation-formatter
description: Estándar para formatear mensajes de texto y conversaciones.
---

# Skill: conversation-formatter

## Purpose
Transforms raw, unstructured conversation logs (e.g., WhatsApp, Telegram, email threads) into clean, readable Obsidian callout blocks.

## Workflow

### 1. Analyze Input
- Identify the participants in the conversation.
- Identify the timestamp format (if present).
- Determine the raw sender identifiers (e.g., phone numbers, email addresses, usernames).

### 2. Normalize Participants
- Map the User (Nico) to `[!quote] Nico`.
- Map the other participant to `[!info] Name` (use the actual name, remove emojis, remove bolding).
- If the participant is unknown, ask the user to identify them before formatting.

### 3. Structure & Format
- Use `> [!info] Name | Timestamp` for the other person.
- Use `> [!quote] Nico | Timestamp` for the user.
- **Grouping:** Merge consecutive messages from the same sender into a single callout block.
- **Cleaning:** Ensure no bolding (`**`) or emojis are present in the callout headers.

### 4. Output
- Return the formatted Markdown block ready to be inserted into the target file.
