---
sidebar_position: 7
---

# Profile Commands Reference

This page covers all commands related to [Openzuma profiles](../user-guide/profiles.md). For general CLI commands, see [CLI Commands Reference](./cli-commands.md).

## `openzuma profile`

```bash
openzuma profile <subcommand>
```

Top-level command for managing profiles. Running `openzuma profile` without a subcommand shows help.

| Subcommand | Description |
|------------|-------------|
| `list` | List all profiles. |
| `use` | Set the active (default) profile. |
| `create` | Create a new profile. |
| `delete` | Delete a profile. |
| `show` | Show details about a profile. |
| `alias` | Regenerate the shell alias for a profile. |
| `rename` | Rename a profile. |
| `export` | Export a profile to a tar.gz archive. |
| `import` | Import a profile from a tar.gz archive. |

## `openzuma profile list`

```bash
openzuma profile list
```

Lists all profiles. The currently active profile is marked with `*`.

**Example:**

```bash
$ openzuma profile list
  default
* work
  dev
  personal
```

No options.

## `openzuma profile use`

```bash
openzuma profile use <name>
```

Sets `<name>` as the active profile. All subsequent `openzuma` commands (without `-p`) will use this profile.

| Argument | Description |
|----------|-------------|
| `<name>` | Profile name to activate. Use `default` to return to the base profile. |

**Example:**

```bash
openzuma profile use work
openzuma profile use default
```

## `openzuma profile create`

```bash
openzuma profile create <name> [options]
```

Creates a new profile.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Name for the new profile. Must be a valid directory name (alphanumeric, hyphens, underscores). |
| `--clone` | Copy `config.yaml`, `.env`, and `SOUL.md` from the current profile. |
| `--clone-all` | Copy everything (config, memories, skills, sessions, state) from the current profile. |
| `--clone-from <profile>` | Clone from a specific profile instead of the current one. Used with `--clone` or `--clone-all`. |
| `--no-alias` | Skip wrapper script creation. |

Creating a profile does **not** make that profile directory the default project/workspace directory for terminal commands. If you want a profile to start in a specific project, set `terminal.cwd` in that profile's `config.yaml`.

**Examples:**

```bash
# Blank profile — needs full setup
openzuma profile create mybot

# Clone config only from current profile
openzuma profile create work --clone

# Clone everything from current profile
openzuma profile create backup --clone-all

# Clone config from a specific profile
openzuma profile create work2 --clone --clone-from work
```

## `openzuma profile delete`

```bash
openzuma profile delete <name> [options]
```

Deletes a profile and removes its shell alias.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to delete. |
| `--yes`, `-y` | Skip confirmation prompt. |

**Example:**

```bash
openzuma profile delete mybot
openzuma profile delete mybot --yes
```

:::warning
This permanently deletes the profile's entire directory including all config, memories, sessions, and skills. Cannot delete the currently active profile.
:::

## `openzuma profile show`

```bash
openzuma profile show <name>
```

Displays details about a profile including its home directory, configured model, gateway status, skills count, and configuration file status.

This shows the profile's Openzuma home directory, not the terminal working directory. Terminal commands start from `terminal.cwd` (or the launch directory on the local backend when `cwd: "."`).

| Argument | Description |
|----------|-------------|
| `<name>` | Profile to inspect. |

**Example:**

```bash
$ openzuma profile show work
Profile: work
Path:    ~/.openzuma/profiles/work
Model:   anthropic/claude-sonnet-4 (anthropic)
Gateway: stopped
Skills:  12
.env:    exists
SOUL.md: exists
Alias:   ~/.local/bin/work
```

## `openzuma profile alias`

```bash
openzuma profile alias <name> [options]
```

Regenerates the shell alias script at `~/.local/bin/<name>`. Useful if the alias was accidentally deleted or if you need to update it after moving your Openzuma installation.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to create/update the alias for. |
| `--remove` | Remove the wrapper script instead of creating it. |
| `--name <alias>` | Custom alias name (default: profile name). |

**Example:**

```bash
openzuma profile alias work
# Creates/updates ~/.local/bin/work

openzuma profile alias work --name mywork
# Creates ~/.local/bin/mywork

openzuma profile alias work --remove
# Removes the wrapper script
```

## `openzuma profile rename`

```bash
openzuma profile rename <old-name> <new-name>
```

Renames a profile. Updates the directory and shell alias.

| Argument | Description |
|----------|-------------|
| `<old-name>` | Current profile name. |
| `<new-name>` | New profile name. |

**Example:**

```bash
openzuma profile rename mybot assistant
# ~/.openzuma/profiles/mybot → ~/.openzuma/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `openzuma profile export`

```bash
openzuma profile export <name> [options]
```

Exports a profile as a compressed tar.gz archive.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to export. |
| `-o`, `--output <path>` | Output file path (default: `<name>.tar.gz`). |

**Example:**

```bash
openzuma profile export work
# Creates work.tar.gz in the current directory

openzuma profile export work -o ./work-2026-03-29.tar.gz
```

## `openzuma profile import`

```bash
openzuma profile import <archive> [options]
```

Imports a profile from a tar.gz archive.

| Argument / Option | Description |
|-------------------|-------------|
| `<archive>` | Path to the tar.gz archive to import. |
| `--name <name>` | Name for the imported profile (default: inferred from archive). |

**Example:**

```bash
openzuma profile import ./work-2026-03-29.tar.gz
# Infers profile name from the archive

openzuma profile import ./work-2026-03-29.tar.gz --name work-restored
```

## `openzuma -p` / `openzuma --profile`

```bash
openzuma -p <name> <command> [options]
openzuma --profile <name> <command> [options]
```

Global flag to run any Openzuma command under a specific profile without changing the sticky default. This overrides the active profile for the duration of the command.

| Option | Description |
|--------|-------------|
| `-p <name>`, `--profile <name>` | Profile to use for this command. |

**Examples:**

```bash
openzuma -p work chat -q "Check the server status"
openzuma --profile dev gateway start
openzuma -p personal skills list
openzuma -p work config edit
```

## `openzuma completion`

```bash
openzuma completion <shell>
```

Generates shell completion scripts. Includes completions for profile names and profile subcommands.

| Argument | Description |
|----------|-------------|
| `<shell>` | Shell to generate completions for: `bash` or `zsh`. |

**Examples:**

```bash
# Install completions
openzuma completion bash >> ~/.bashrc
openzuma completion zsh >> ~/.zshrc

# Reload shell
source ~/.bashrc
```

After installation, tab completion works for:
- `openzuma profile <TAB>` — subcommands (list, use, create, etc.)
- `openzuma profile use <TAB>` — profile names
- `openzuma -p <TAB>` — profile names

## See also

- [Profiles User Guide](../user-guide/profiles.md)
- [CLI Commands Reference](./cli-commands.md)
- [FAQ — Profiles section](./faq.md#profiles)
