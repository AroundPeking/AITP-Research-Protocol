---
name: skill-init
description: First-run setup — ask the user where to store research topics and save workspace config.
trigger: no_topics_root_configured
---

# First-Run Workspace Setup

This is the first time AITP is running in this workspace. You need to configure
where research topics will be stored.

## MANDATORY: AskUserQuestion

You MUST use AskUserQuestion to ask the user where to store topics. Load the tool:

1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load it.
2. Call `AskUserQuestion` with the question below.

### What to ask

Present these options (adapt the paths to the detected workspace root):

> **Where should AITP store research topics?**
>
> - `<workspace>/topics/` — recommended, keeps topics in the workspace root
> - `<workspace>/research/aitp-topics/` — traditional location
> - Custom path — specify any directory

The default and recommended choice is `<workspace>/topics/`.

## After the user answers

1. **Create the directory** if it doesn't exist:
   ```python
   os.makedirs(chosen_path, exist_ok=True)
   ```

2. **Write `.aitp_config.json`** in the workspace root:
   ```json
   {
     "topics_root": "<relative or absolute path to chosen directory>",
     "initialized_at": "<ISO timestamp>"
   }
   ```

   Use a relative path from the workspace root if possible (e.g., `"topics"` or
   `"research/aitp-topics"`). This makes the config portable across machines.

3. **Create the topics directory structure**:
   - The chosen directory itself will hold topic subdirectories
   - No need to create individual topics yet — that happens via `aitp_bootstrap_topic`

4. **Confirm to the user**:
   Tell them the config is saved and they can start using AITP. The next session
   will automatically detect the topics root.

## Config file location

The config file is always at `<workspace_root>/.aitp_config.json`. The workspace
root is detected by walking up from cwd looking for `.git`, `CLAUDE.md`, or the
config file itself.

## Environment variable override

If `AITP_TOPICS_ROOT` is set, it takes priority over the config file. This is
useful for CI or non-interactive environments.

## Allowed transitions after init

Once the config is saved, the user can:
- Bootstrap a new topic with `aitp_bootstrap_topic`
- List topics with `aitp_list_topics`

The session_start hook will automatically detect the configured topics root
on subsequent sessions.
