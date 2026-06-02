# Color Coaster — 4-Color Multi-Material Test Print

Round coaster with a 4-color face design. The face has a grey center circle with
the outer ring split yellow (top half) and red (bottom half). The underside and
coaster bulk are solid black. A useful calibration print for verifying multi-material
color registration and layer transition quality.

## Dimensions

| Parameter | Value |
|---|---|
| Diameter | 88.9 mm (3.5") |
| Thickness | 4 mm |
| Grey center diameter | 25.4 mm (1") |
| Face color depth | 1 mm |
| Chamfer | 1 mm (45°, top outer edge) |

## Run

```bash
uv run python projects/color-coasters/model.py
```

No arguments — all parameters are at the top of `model.py`.

## Customization

Edit these variables in `model.py`:

| Variable | Default | Description |
|---|---|---|
| `diameter` | `inches_to_mm(3.5)` | Overall diameter |
| `thickness` | `4.0` | Overall thickness (mm) |
| `grey_diameter` | `inches_to_mm(1.0)` | Grey center circle diameter |
| `chamfer_size` | `1.0` | Chamfer on top outer edge (mm) |
| `face_depth` | `1.0` | Depth of colored face region (mm) |

## Print Settings

| Setting | Value |
|---|---|
| Printer | Any multi-material FDM printer |
| Material | PLA or PETG |
| Nozzle | 0.4 mm |
| Layer height | 0.20 mm |
| Orientation | **Face-down on textured plate** (flip upside down in slicer) |
| Supports | None — flat disc, no overhangs |

The decorative face is modeled face-up (Z+) but printed face-down for a smooth
finish from the textured build plate.

## Colors / Materials

| Color | Body | Layers |
|---|---|---|
| Grey | Center circle (25.4 mm dia) | Top 1 mm only |
| Yellow | Top half of outer ring | Top 1 mm only |
| Red | Bottom half of outer ring | Top 1 mm only |
| Black | Underside + bulk | Z = 1–4 mm |

## Slicer Workflow

Import the individual STL files as separate objects and assign each a different
extruder/material in your slicer:

| File | Color |
|---|---|
| `exports/color-coaster_grey.stl` | Grey |
| `exports/color-coaster_yellow.stl` | Yellow |
| `exports/color-coaster_red.stl` | Red |
| `exports/color-coaster_black.stl` | Black |

## Files

- `model.py` — parametric source
- `exports/color-coaster_grey.stl`
- `exports/color-coaster_yellow.stl`
- `exports/color-coaster_red.stl`
- `exports/color-coaster_black.stl`
- `exports/color-coaster.step` — archival CAD file
