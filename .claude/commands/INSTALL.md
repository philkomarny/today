# How to install the /today command

The `today.md` file next to this one is a Claude Code custom slash command. For `/today` to work, it needs to be copied to YOUR project's `.claude/commands/` directory — not left inside `daily-briefing/`.

## Setup

```bash
# From your project root (where you run Claude Code):
mkdir -p .claude/commands
cp daily-briefing/.claude/commands/today.md .claude/commands/today.md
```

That's it. Now when you open Claude Code in this directory and type `/today`, it will run the daily briefing system.

## How it works

Claude Code looks for `.md` files in `.claude/commands/` and registers them as slash commands. The filename becomes the command name — so `today.md` becomes `/today`.

The content of `today.md` is a one-line instruction that tells Claude to read and execute the full orchestrator at `daily-briefing/commands/today-v2.md`.

## If you renamed the folder

If you put the system in a folder other than `daily-briefing/`, edit `today.md` to match:

```markdown
Read and execute the orchestrator at `YOUR-FOLDER-NAME/commands/today-v2.md`. Follow every instruction in that file exactly.
```
