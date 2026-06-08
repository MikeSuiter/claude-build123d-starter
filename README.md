# claude-build123d-starter

A ready-to-use project template for creating parametric 3D CAD models with
[build123d](https://build123d.readthedocs.io/) and [Claude Code](https://claude.ai/code).
Supports 3D printing (FDM/SLA), CNC milling/routing, laser cutting, and reference geometry.

Describe what you want to model in plain English — Claude writes the Python code,
shows a live 3D preview, and exports files ready for your fabrication workflow. No CAD experience required.

## How It Works

- **[build123d](https://build123d.readthedocs.io/)** — Python library for creating parametric 3D models programmatically
- **[Claude Code](https://claude.ai/code)** — Anthropic's AI coding assistant; reads the project instructions and writes/runs the model code for you
- **[OCP CAD Viewer](https://marketplace.visualstudio.com/items?itemName=bernhard-42.ocp-vscode)** — VS Code extension that shows a live 3D preview as models are built

---

## Prerequisites

### 1. uv — Python package manager

uv installs and manages Python automatically — no separate Python install needed.

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Or with Homebrew: `brew install uv`

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Or with winget: `winget install --id=astral-sh.uv -e`

### 2. VS Code + OCP CAD Viewer

1. Install [VS Code](https://code.visualstudio.com/)
2. Open VS Code, go to the Extensions panel (Ctrl+Shift+X / Cmd+Shift+X), search for **OCP CAD Viewer**, and install it

### 3. Claude Code

Follow the install instructions at [claude.ai/code](https://claude.ai/code). When done, verify it works:

```bash
claude --version
```

### 4. Fabrication hardware (optional)

Any 3D printer (FDM/SLA), CNC router/mill, or laser cutter. You can view, model, and export without any hardware at all.

---

## Setup

### 1. Clone the repo and install dependencies

```bash
git clone https://github.com/MikeSuiter/claude-build123d-starter my-cad-models
cd my-cad-models
uv sync
```

`uv sync` creates a virtual environment and installs build123d and all other dependencies. It runs in seconds.

### 2. Open the project in VS Code

```bash
code .
```

Or open VS Code manually and use **File → Open Folder**, then select the `my-cad-models` folder.

After it opens, click the **OCP CAD Viewer** icon in the left sidebar to open the 3D preview panel. You'll see it there once a model runs.

### 3. Configure your machine work envelope (optional)

Edit `lib/helpers.py` and set `BUILD_VOLUME` to your machine's work area (printer bed, CNC travel envelope, or laser bed). Claude will use this to validate models fit before exporting.

```python
# Examples:
BUILD_VOLUME = (256, 256, 256)  # Bambu Lab P2S
BUILD_VOLUME = (235, 235, 250)  # Ender 3
BUILD_VOLUME = (250, 210, 220)  # Prusa MK4
BUILD_VOLUME = (600, 900, 80)   # Typical hobby CNC router
BUILD_VOLUME = (400, 300, 0)    # Typical desktop laser cutter (Z unused)
```

Skip this step if you haven't settled on a machine yet.

### 4. Verify everything works

You'll run two terminals inside VS Code (**Terminal → New Terminal**, then use the split button to add a second).

**Terminal 1 — start the 3D viewer (keep this running):**
```bash
uv run python start_viewer.py
```

**Terminal 2 — run the example model:**
```bash
uv run python projects/color-coasters/model.py
```

The OCP CAD Viewer panel should display a 4-color US flag coaster. If the panel is blank, make sure Terminal 1 is running first — it's the local server the viewer connects to.

---

## Creating Your First Model

With the viewer running in Terminal 1, open a new terminal and launch Claude Code:

```bash
claude
```

Claude automatically reads `CLAUDE.md` on startup — it knows the project conventions and best practices. Use the `/new-project` slash command — Claude will ask a few focused questions (what to build, dimensions, material, colors), then write the model code, run it, and verify it displays in the viewer.

Or just describe what you want directly:

> "Make a wall-mount phone holder, about 4 inches wide, printed in black PETG"

> "Design a finger-jointed box lid for CNC routing, 200 × 150mm, in 18mm plywood"

> "Laser-cut a living-hinge card holder in 3mm acrylic, 90 × 60mm"

Claude follows an incremental workflow: base geometry first, features one at a time, colors last. You'll see the model update in the OCP CAD Viewer as each step completes.

---

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
    ├── _template/                # Starting point for new projects
    │   └── model.py
    ├── color-coasters/           # Example: 4-color US flag coaster (FDM → STL)
    │   ├── model.py
    │   ├── README.md
    │   └── exports/
    ├── cnc-coasters/             # Example: US flag coaster vector outlines (CNC/laser → DXF)
    │   ├── model.py
    │   ├── README.md
    │   └── exports/              # cnc-coasters.dxf (3 layers: PERIMETER, STAR, TEXT)
    ├── gear-pair/                # Example: meshing involute spur gear pair (FDM/reference)
    │   ├── model.py
    │   ├── README.md
    │   └── exports/
    ├── finger-joint-frame/       # Example: 4-panel finger-joint box frame (CNC → DXF)
    │   ├── model.py
    │   ├── README.md
    │   └── exports/              # front_back.dxf, left_right.dxf, assembly.step
    └── mountain-range/           # Example: smooth 4-peak terrain relief (CNC → STEP)
        ├── model.py
        ├── README.md
        └── exports/              # mountain-range.step, mountain-range.stl
```

---

## Links

- [build123d documentation](https://build123d.readthedocs.io/)
- [build123d GitHub](https://github.com/gumyr/build123d)
- [OCP CAD Viewer extension](https://marketplace.visualstudio.com/items?itemName=bernhard-42.ocp-vscode)
- [uv — Python package manager](https://docs.astral.sh/uv/)
- [Claude Code](https://claude.ai/code)
