# CLAUDE.md — build123d CAD Project Instructions

## Session Startup

**At the start of every session, read `LEARNINGS.md`** — it contains accumulated
discoveries from past projects (API gotchas, SVG workflow tips, design patterns).
**At the end of any session where something new was discovered, update `LEARNINGS.md`.**

## Project Overview

This repo contains parametric 3D CAD models built with build123d (Python).
Each model lives in its own folder under `projects/`. Models may target any
fabrication method — 3D printing (FDM/SLA), CNC milling/routing, laser cutting,
or reference/visualization only.

## Environment

- Python managed by `uv` — always use `uv run` to execute scripts
- VS Code with ocp-vscode extension for live 3D preview
- Run models with: `uv run python projects/<project>/model.py`

---

## Critical Rules

### Units

- **Model in millimeters** for all projects.
- If the user provides dimensions in inches, convert to mm in the parameters
  section and comment the original inch value:
  ```python
  width = 25.4  # 1 inch
  height = inches_to_mm(2.5)  # 2.5 inches
  ```
- Always note the unit system in the file docstring.
- Comment dimensions with their purpose: `width = 88.9  # 3.5" — cabinet face width`

### Code Style

- Use **Algebra mode** (not Builder mode) as the default. It's stateless and
  easier to reason about. Only use Builder mode if the geometry genuinely benefits from it.
- **Import only what you use** from build123d (avoid wildcard imports).
  Example: `from build123d import Box, Cylinder, chamfer, Color, Align`
- All dimensions must be **parameterized as named variables** at the top of the file.
  Never hard-code numbers inline in geometry operations.
- Group code into clear sections:
  ```
  # === Parameters ===
  # === Print Settings ===
  # === Model ===
  # === Display ===
  # === Validation ===
  # === Export ===
  ```
- **Delay fillets and chamfers** until the end of the model — build123d best practice.
- **Start with 2D sketches**, then extrude/revolve to 3D.
- Always include `show()` from ocp_vscode for live preview.

### File Organization

- One model per `projects/<project-name>/model.py`
- Exports go in `projects/<project-name>/exports/`
- Each project gets a `README.md` with description, dimensions, and print settings
- Shared utilities in `lib/helpers.py` — do not duplicate helper logic
- To start a new project: copy `projects/_template/` to `projects/<new-name>/`

---

## Workflow: Start Small, Iterate

**Do NOT try to build the entire model in one shot.** Instead:

1. **Start with the base geometry** — the simplest shape (e.g., a cylinder for
   a coaster, a box for an enclosure). Get it running and displaying in ocp-vscode.
2. **Add one feature at a time** — chamfers, fillets, holes, pockets, etc.
   Run and verify visually after each addition.
3. **Add color bodies last** — once the geometry is correct, split into separate
   bodies for multi-color if needed.
4. **Add export last** — only after the model looks right in the viewer.

---

## Asking Questions First

**Before writing ANY model code, ask the user only the questions you actually
need answers to (skip anything already provided or that has a sensible default):**

1. **What are the overall dimensions?** (length × width × height or diameter × height)
2. **What units are you thinking in?** (default: mm, will convert either way)
3. **What is the fabrication method?**
   - 3D print (FDM/SLA) — need printer + build volume, wall thickness, overhang limits
   - CNC mill/router — need tool diameter, stock dimensions, dogbone corners
   - Laser cut — need material thickness, kerf compensation
   - Reference/visualization only — fewer constraints
4. **How many colors/materials?** (multi-material printers — which parts get which color?)
5. **Any mating/fit surfaces?** (tolerances — press fit, slip fit, clearance)
6. **What material?** (PLA, PETG, TPU, wood, aluminum, etc.)

### Additional questions for 3D printing

- Printer make/model and build volume?
- Nozzle size? (affects minimum wall/feature size — default: 0.4mm)
- Print orientation preference?
- Supports acceptable or design to avoid them?

### Additional questions for CNC

- Tool diameter? (affects inside corner radii, dogbone relief)
- Stock dimensions and material?
- 2.5D or full 3D toolpaths?
- Fixturing / workholding approach?
- Joinery type? (pocket, dado, mortise & tenon, dovetail, finger joint)

### Additional questions for laser cutting

- Material and thickness?
- Kerf width for compensation?
- Living hinges or bend features?

---

## 3D Printing Context

### General FDM Rules

- **Minimum wall thickness**: 0.8mm (2 perimeters @ 0.4mm nozzle), prefer 1.2mm+
- **Minimum hole diameter**: 2mm for clean through-holes
- **Hole compensation**: Holes print ~0.2-0.4mm undersized; add 0.2mm to radius
- **Bridge length**: Keep unsupported spans under 10mm
- **Overhang angle**: Up to 45 degrees without supports
- **Chamfer bottom edges** instead of fillet where part meets bed — prints cleaner
- **Elephant foot**: First layer widens ~0.1-0.2mm; account for on mating surfaces
- **Flat bottom preferred**: Design a flat surface for bed adhesion
- **Clearance for fits**: 0.3mm gap for slip fit, 0.1mm for press fit
- **Text/embossing**: Minimum 0.6mm extrude depth, ~8pt minimum font equivalent

### Orientation

Model decorative face on top (Z+). User flips in slicer when needed. Note intended
orientation in README.

### Multi-Color / Multi-Material

- Each color must be a **separate body/solid** in the model
- Assign `.color` and `.label` to each body before export
- Design color boundaries at layer transitions where possible (cleaner result)
- Avoid tiny color regions smaller than ~2mm — filament swaps have purge waste
- For text/logos on a surface: model as a separate body with slight extrusion
  (0.4-0.8mm) or inset cut, then assign a different color

### Build Volume

Set `BUILD_VOLUME` in `lib/helpers.py` to your printer's build volume (X, Y, Z in mm),
then call `check_build_volume(part)` before exporting to verify fit.

---

## Export Strategy

- **Single-color**: `export_all(part, "name")` → STL + STEP + preview
- **Multi-color**: `export_multicolor([bodies...], "name")` → individual STLs per body + STEP
- STEP is the archival/interchange format — always include it.
- STL for slicers and CAM software.
- Assign `.color` and `.label` to each body before calling `export_multicolor()`

```python
# Single-color
from lib.helpers import export_all
export_all(part, "project-name", output_dir=EXPORT_DIR)

# Multi-color
from build123d import Color
from lib.helpers import export_multicolor
body_a.color = Color("black"); body_a.label = "base"
body_b.color = Color("red");   body_b.label = "accent"
export_multicolor([body_a, body_b], "project-name", output_dir=EXPORT_DIR)
```

---

## Importing and Using SVG Files

Use `import_svg()` for logos and vector art. **See LEARNINGS.md for the full SVG workflow and gotchas.**

Key points:
- Always use `align=None` to preserve SVG coordinate positions
- Returns `ShapeList[Wire | Face]` — filter by type as needed
- Set `flip_y=True` if SVG coordinates appear inverted
- Use bounding box calculations to center/position after import
- **NEVER drop SVG paths** — if some don't import, check the SVG prep workflow in LEARNINGS.md
- If user provides a broken SVG: Ungroup All, Object to Path, Stroke to Path, Simplify, save as Plain SVG

---

## Modeling Best Practices

- **2D before 3D**: Create sketches first, then extrude/revolve
- **Delay chamfers and fillets** until the end — they add complexity to topology
- **Parameterize everything** — derive secondary dimensions from key variables
- **Avoid self-intersecting geometry**
- Use selectors (`.faces()`, `.edges()`, `.filter_by()`, `.sort_by()`,
  `.group_by()`) to pick geometry for operations
- For assemblies, use shallow copies for repeated components
- If OpenCascade fails on a geometry operation, try an alternative approach
  (e.g., loft instead of sweep, simpler sketch, different operation order).
  OpenCascade kernel errors are common — don't just retry the same thing.

### CNC-Specific Patterns

```python
# Dogbone relief at inside corners for CNC pockets
tool_radius = 3.175  # 1/8" bit
# Add relief circles at each inside corner offset by tool_radius
```

---

## Testing a Model

```bash
uv run python projects/<project>/model.py
```

The ocp-vscode viewer updates live if the extension is running.

---

## Model Complexity Guidelines (Haiku vs Sonnet)

| Haiku | Sonnet |
|---|---|
| Simple primitives, basic ops | Complex/organic shapes |
| Dimension changes, bug fixes | Multi-body assemblies |
| Single-color models | Multi-color models |
| Simple 2D sketches + extrusions | Complex sketches (splines, arcs) |
| Export/display code additions | Sweep/loft operations |
| Parametric variations | SVG import + boolean ops |
| | Failed model rethinks, new complex projects |

---

## Starting a New Project

**Start new projects in normal mode**, not plan mode. Plan mode front-loads too
much complexity and burns context on planning that drifts during implementation.

Instead, follow the incremental workflow:

1. Ask only the essential questions you need answered
2. Build the base geometry first — get it running and visible
3. Add features one at a time, verifying each step
4. Add color separation after geometry is correct
5. Add export as the final step

**Use plan mode only for** genuinely complex assemblies, multi-part projects,
or models with intricate spatial relationships that need upfront reasoning.

---

## Common Patterns

### Box with rounded vertical edges

```python
part = Box(length, width, height)
part = fillet(part.edges().filter_by(Axis.Z), radius)
```

### Plate with countersunk holes

```python
plate = Box(length, width, thickness)
plate -= Pos(x, y) * CounterSinkHole(hole_radius, cs_radius, depth)
```

### Revolved profile (e.g., knob, bowl)

```python
with BuildSketch(Plane.XZ) as profile:
    # draw half-profile, then revolve
    ...
part = revolve(profile.sketch, axis=Axis.Z, revolution_arc=360)
```

### Snap-fit cantilever clip

```python
# Cantilever beam with angled catch
# Rule of thumb: deflection ~0.3mm, beam length > 10× thickness
```

### Parametric hole pattern

```python
from build123d import Cylinder, Pos
hole = Cylinder(hole_r, thickness)
for x, y in hole_positions:
    part -= Pos(x, y) * hole
```
