# claude-build123d-starter

A ready-to-use project template for creating parametric 3D CAD models with
[build123d](https://build123d.readthedocs.io/) and [Claude Code](https://claude.ai/code).

Open this project in Claude Code, describe what you want to model, and it will write
the Python code, show a live 3D preview, and export print-ready files.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager (installs Python 3.12 automatically)
- [VS Code](https://code.visualstudio.com/) with the [OCP CAD Viewer](https://marketplace.visualstudio.com/items?itemName=bernhard-42.ocp-vscode) extension
- [Claude Code](https://claude.ai/code)
- Any FDM/SLA 3D printer (optional — you can view and export models without printing)

### Install uv

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Or with Homebrew: `brew install uv`

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Or with winget: `winget install --id=astral-sh.uv -e`

## Quick Start

```bash
git clone https://github.com/your-username/claude-build123d-starter my-cad-models
cd my-cad-models
uv sync
```

Open VS Code, then in two terminals:

```bash
# Terminal 1: start the 3D viewer
uv run python start_viewer.py

# Terminal 2: run the example model
uv run python projects/color-coasters/model.py
```

The OCP CAD Viewer panel in VS Code will show the model live.

## Using with Claude Code

```bash
claude  # open Claude Code in this directory
```

Claude automatically reads `CLAUDE.md` on startup — it knows the project conventions,
code style, and best practices. Then just describe what you want:

> "Make a wall-mount phone holder, about 4 inches wide, printed in black PETG"

Or use the built-in `/new-project` slash command — Claude will ask a few targeted
questions (dimensions, material, colors), then write the model code, run it, and
verify it displays correctly.

## Configure Your Printer

Edit `lib/helpers.py` and set `BUILD_VOLUME` to your printer's dimensions:

```python
# Examples:
BUILD_VOLUME = (256, 256, 256)  # Bambu Lab P2S
BUILD_VOLUME = (235, 235, 250)  # Ender 3
BUILD_VOLUME = (250, 210, 220)  # Prusa MK4
```

After that, `check_build_volume(part)` will validate models fit before export.

## Project Structure

```
.
├── CLAUDE.md                     # AI instructions (auto-loaded by Claude Code)
├── LEARNINGS.md                  # Accumulated build123d tips and API gotchas
├── start_viewer.py               # Launch the OCP CAD Viewer server
├── .claude/commands/
│   └── new-project.md            # /new-project slash command
├── lib/
│   └── helpers.py                # Shared export and utility functions
├── fonts/                        # Oswald + Space Mono fonts for text geometry
└── projects/
    ├── _template/                # Copy this to start a new project
    │   └── model.py
    └── color-coasters/           # Example: 4-color multi-material coaster
        ├── model.py
        ├── README.md
        └── exports/
```

## Creating a New Model

```bash
# Copy the template
cp -r projects/_template projects/my-thing

# Open Claude Code
claude
```

Then either use `/new-project` or just describe what you want to build. Claude follows
the incremental workflow: base geometry first, features one at a time, colors last.

## Links

- [build123d documentation](https://build123d.readthedocs.io/)
- [build123d GitHub](https://github.com/gumyr/build123d)
- [OCP CAD Viewer extension](https://marketplace.visualstudio.com/items?itemName=bernhard-42.ocp-vscode)
- [uv — Python package manager](https://docs.astral.sh/uv/)
- [Claude Code](https://claude.ai/code)
