# LEARNINGS — build123d Project Discoveries

Running log of discoveries made during real projects. Read this at the start of
each session to apply accumulated knowledge. Update it when something new is
found — good or bad.

---

## build123d API

### `scale()` uses `by=`, not `factor=`
```python
# WRONG — throws TypeError
logo_scaled = scale(logo, factor=0.5)

# CORRECT
logo_scaled = scale(logo, by=0.5)
```

### Chamfer edge selection by Z position
```python
base.edges().sort_by(Axis.Z)[0]   # bottom edge (lowest Z)
base.edges().sort_by(Axis.Z)[-1]  # top edge (highest Z)
```

### Embossing Text on a face — correct Plane orientation

Face orientation determines `z_dir` and extrude sign. Use the wrong combo and
text appears mirrored, flipped, or cuts in the wrong direction.

**Bottom face (Z=0), cutting upward into part:**
```python
# z_dir=(0,0,-1): normal points down (away from part). Negative amount = cut in +Z.
label_sketch = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 0, -1)) * Text(...)
label_solid = extrude(label_sketch, amount=-label_depth)
part = part - label_solid
```

**Top face (Z=thickness), cutting downward into part:**
```python
# z_dir=(0,0,1): normal points up (toward viewer). Negative amount = cut in -Z.
label_sketch = Plane(origin=(x, y, thickness), x_dir=(1, 0, 0), z_dir=(0, 0, 1)) * Text(...)
label_solid = extrude(label_sketch, amount=-label_depth)
part = part - label_solid
```

Key rules:
- **Never use `Pos()` or `.translate()` to reposition a text solid** — they silently
  fail in ocp_vscode (solid renders at origin or not at all). Create the sketch on
  a correctly-offset `Plane` instead.
- **Never use `.mirror(Plane.YZ)`** — `Plane.YZ` is a property that returns the wrong
  type; define the plane explicitly.
- **`bolt_part.solids()[0]`** only returns the first solid and will drop text letter
  solids if text is added via `+`. Subtract text from the head before assembling
  the bolt, so the subtraction is baked into the head solid.
- Text solid bounding box must overlap the target solid — verify with
  `print(label_solid.bounding_box())` before subtracting.

---

## SVG Workflow

### Affinity Designer 3 — fixing compound path holes
If a logo has outlined/stroked paths that create hollow areas (compound paths
with inner holes), right-click the object and choose **Fill Holes**. This fills
inner cutouts in one click without restructuring the paths.

### Affinity Designer 3 — thin strokes that won't print
If logo elements have very thin strokes (arrow shafts, fine lines):
1. Set stroke width to at least 21px (≈1mm at 1486px → 70mm scale)
2. Right-click > **Expand Stroke** to convert stroke to filled geometry
3. Re-export as plain SVG

### SVG scale math
To check if SVG paths will be thick enough to print:
```
mm_per_px = target_width_mm / svg_canvas_width_px
stroke_width_mm = stroke_width_px * mm_per_px
```
Minimum printable width is 0.4mm (1 perimeter). Prefer 0.8mm+.
Example: 1486px canvas → 70mm = 0.047mm/px. A 2px stroke = 0.094mm — won't print.

### SVG paths extend far outside the canvas — scale by canvas size, clip per-face

SVGs with per-path `matrix(...)` transforms can import with a bounding box much
larger than the canvas (e.g. 845×845px canvas → 1973×3343 in build123d space).
**Never scale using the imported bounding box** — it gives wrong proportions and
the out-of-canvas geometry causes compound boolean operations to hang or fail.

**Correct approach:**
1. Read canvas size from the SVG `width`/`height` attributes.
2. Scale with `svg_scale = logo_target_width / svg_canvas_px`.
3. Center on canvas center (with `flip_y=True`: cx = logo/2, cy = -logo/2).
4. **Clip and extrude each face individually** (not as a compound) before unioning:
   ```python
   logo_clip = Pos(0, 0, top_z - h/2) * Cylinder(ring_inner_r, h * 2)
   bodies = []
   for face in blue_faces:
       body = extrude(offset * scale(face, by=svg_scale), amount=h) & logo_clip
       bodies.append(body)
   logo_body = bodies[0]
   for b in bodies[1:]: logo_body = logo_body + b
   ```
   Per-face clip is fast. Clipping or boolean-ing a compound of many SVG faces hangs.

### `import_svg` without `flip_y=True` gives negative Y coordinates

SVG y=0 (top) maps to build123d y=0; SVG y=148 (bottom) maps to y=–148 (negated,
not flipped). After scaling, shapes sit at y=–height..0. Placing them with
`Pos(0, target_cy)` shifts them correctly in X but leaves the y offset wrong —
the shapes end up ~height/2 lower than expected, with dead space above.

**Always normalize the bounding box before positioning any SVG import:**
```python
tree_shapes = import_svg(SVG_PATH, align=None)
scaled = [s.scale(scale_factor) for s in tree_shapes]
tree_raw = Compound(children=scaled)          # NOT shape + shape (gives ShapeList, no .bounding_box())
bb = tree_raw.bounding_box()
cx = (bb.min.X + bb.max.X) / 2
# Put tree top at y=0, then place at desired top position:
tree_normalized = tree_raw.translate((-cx, -bb.max.Y, 0))
tree_body = Pos(0, total_h - top_margin, z) * extrude(tree_normalized, depth)
```

Key rules:
- `shape + shape` returns a `ShapeList` — no `.bounding_box()`. Use `Compound(children=[...])`.
- Normalize top (`-bb.max.Y`) for top-anchored placement, bottom (`-bb.min.Y`) for bottom-anchored.
- Use the actual bb dimensions for layout variables (e.g. `text_h`), not assumed values.

### White paths often don't need subtraction on a white base
If the coaster/base color matches the SVG's "background" color (e.g. white base,
white SVG paths), skip the boolean subtraction entirely. White areas show through
naturally where there's no blue path. Only subtract if the background color differs.

---

## Multi-Color / Inlay Design

### Flush inlay vs raised logo
- **Raised** (logo extruded above surface): simpler, but logo sits proud of base
- **Flush inlay** (logo cut into base): cleaner look, logo is level with surface

For flush inlay:
```python
# Extrude logo starting below top surface
logo_positioned = Pos(-cx, -cy, top_z - logo_extrude_height) * logo_scaled
logo_3d = extrude(logo_positioned, amount=logo_extrude_height)
# Cut pocket into base
base = base - logo_3d
# Now logo_3d fills the pocket flush with the top face
```

---

## Multi-Color Export

### Skip 3MF — use individual STLs for multi-color slicing
Do NOT generate a combined 3MF for multi-color prints unless explicitly requested.
The Mesher creates one mesh object per sub-solid in a Compound, resulting in
hundreds of unnamed objects when the logo has many SVG paths. Individual STLs
are the correct workflow for multi-material slicers.

Export pattern (no 3MF):
```python
export_stl(base,   str(EXPORT_DIR / f"{name}_base_black.stl"))
export_stl(yellow, str(EXPORT_DIR / f"{name}_band_yellow.stl"))
# ... etc.
export_step(Compound(children=bodies), str(EXPORT_DIR / f"{name}.step"))
```

---

## SVG Logo Import — Paint-Order / Letter Counters

### Black paths that appear AFTER the last white path must NOT be subtracted
When a logo has letter counters (the inner black shapes inside letters like G, A, R),
those counters are painted last in the SVG (higher path index) and appear on top of
the white letter paths. Subtracting all white shapes from all black shapes removes them.

Fix: split black paths into two groups by comparing path index to `last_white_index`:
- **Background blacks** (index ≤ last_white_index): subtract white from these
- **Top-layer blacks** (index > last_white_index): extrude as-is, no subtraction

```python
# Determine split point
last_white_index = max(i for i, fill in enumerate(path_fills) if fill == "white")
background_blacks = {i for i in black_indices if i <= last_white_index}
toplayer_blacks   = {i for i in black_indices if i >  last_white_index}

black_logo = (extrude(background_blacks) - extrude(white_paths)) + extrude(toplayer_blacks)
```

---

## Reusable Library Patterns

### `lib/helpers.py` — `FONTS_DIR` constant
Points to `fonts/` at repo root. Import and use with `Text(font_path=...)`:
```python
from lib.helpers import FONTS_DIR
font_bold = str(FONTS_DIR / "Oswald-Bold.ttf")
Text("hello", font_size=8.0, font_path=font_bold, align=(Align.CENTER, Align.CENTER))
```

### `export_step` — "Unknown Compound type, color not set" warning
Algebra-mode shapes (boolean ops, `extrude(Text(...))`) are flat OCC Compounds with
no build123d `.children`. `export_step` walks the shape tree and can only apply color
to `Part`, `Sketch`, and `Curve` subclasses — plain Compounds trigger this warning.
The STEP exports correctly; color is just not embedded. Already suppressed in
`export_multicolor`. Do NOT set `.color` on wrapper compounds passed to `export_step`.

---

## Parametric Text Layout

### Auto-fitting font size to a target width
Measure the actual `Text()` bounding box and iterate down until it fits.
Reliable because it uses the real rendered metrics, not estimated char widths:
```python
def fit_size(content, max_size, step=0.1):
    size = max_size
    while size > 2.0:
        if Text(content, font_size=size, font_path=FONT,
                align=(Align.CENTER, Align.CENTER)).bounding_box().size.X <= max_w:
            return size
        size -= step
    return size
```

### Equal vertical spacing from measured text heights
Solve for gap algebraically — works for any number of lines:
```python
def measure_h(content, size):
    return Text(content, font_size=size, font_path=FONT,
                align=(Align.CENTER, Align.CENTER)).bounding_box().size.Y

year_h  = measure_h(str(year), year_size)
award_h = measure_h(award,     award_size)
name_h  = measure_h(name,      name_size)

# n_lines + 1 equal gaps (top + between each + bottom)
gap = (plate_h - year_h - award_h - name_h) / 4

y_year  =  plate_h/2 - gap - year_h/2
y_award =  plate_h/2 - gap - year_h  - gap - award_h/2
y_name  =  plate_h/2 - gap - year_h  - gap - award_h - gap - name_h/2
```

### Font size conversion: Affinity Designer → build123d
`1pt = 0.3528mm` — multiply Affinity pt size by 0.3528 for build123d `font_size`.
Example: 22.5pt → 7.94mm, 30pt → 10.58mm.

---

## Multi-Model Projects (Shared Params + Combined Preview)

### Structure for related models that share geometry
When two models mate physically (e.g. base + snap-in insert), use this pattern:
1. `shared_params.py` at the project folder level — all shared dims live here
2. Each model file exposes a `build_*()` function returning the color bodies
3. Guard argparse with `if __name__ == "__main__"` so files are safely importable
4. Create a `model.py` that imports both build functions, assembles them in world space, and calls `show()` + exports

```python
# model.py — combined preview + export
from base import build_base
from insert import build_insert

plaque, red_lip = build_base()
insert_body, text_body = build_insert()

show(plaque, red_lip, insert_body, text_body)
export_multicolor([plaque, red_lip], "base", output_dir=EXPORT_DIR)
export_multicolor([insert_body, text_body], "insert", output_dir=EXPORT_DIR)
```

### shared_params.py import path
Add `sys.path.insert(0, str(Path(__file__).parent.parent))` to each model file so
it can find `shared_params.py` one directory up.

### Ordering matters in shared_params.py
If a derived value depends on another variable, it must be defined after it.
Symptom: `NameError: name 'X' is not defined`.

---

## build123d Alignment Gotcha — `Pos() * Box()` uses CENTER alignment by default

When placing a `Box` with `Pos()`, the default `align=(Align.CENTER, Align.CENTER, Align.CENTER)`
means `Pos(x, y, z)` moves the **center** of the box to that point — not the corner.

**Wrong (center of void ends up at the specified corner position):**
```python
void = Pos(x_start, y_start, -1) * Box(width, height, thickness + 2)
# → box center at (x_start, y_start, -1), NOT min-corner
```

**Correct (min-corner of void at the specified position):**
```python
void = Pos(x_start, y_start, -1) * Box(
    width, height, thickness + 2,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
```

Symptom: subtracted voids remove far less volume than expected. Caught by comparing
`frame.volume` to hand-calculated expected volume.

---

## Stadium / Capsule Shape

### Use `SlotCenterToCenter` — not `RectangleRounded` — for pill shapes
`RectangleRounded(w, h, r)` requires strict `w > 2*r` AND `h > 2*r`.
When `r = h/2` (perfect semicircle ends), it throws `ValueError: width and height must be > 2*radius`.

Use `SlotCenterToCenter(center_separation, height)` instead:
```python
# center_separation = total_width - height  (distance between arc centers)
insert_body = extrude(
    Plane(origin=(0, insert_h / 2, 0)) * SlotCenterToCenter(insert_w - insert_h, insert_h),
    amount=insert_t,
)
```
Position the Plane at `(0, height/2, 0)` to align Y from 0 → height (matching `Align.MIN`).

### Fillet fails when radius = half the perpendicular span
OCC raises `ValueError: Failed creating a fillet with radius of X` when the radius
equals or approaches the half-height of the edge being filleted. Switch to sketch-based
approach (`SlotCenterToCenter` or `RectangleRounded`) instead of `Box + fillet`.

---

## Typography

### Middot `·` (U+00B7) centers better than `|` for all-caps text
The pipe `|` has full ascender/descender height, making it look top-heavy between
all-caps words. The middot sits at optical mid-height and reads as balanced:
```python
STATS_LINE = "  ·  ".join(_parts)  # not "  |  "
```
