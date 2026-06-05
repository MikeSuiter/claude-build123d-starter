# CNC Coaster — Vector Outlines for CNC/Laser

Round coaster with three vector layers ready for CAM. The perimeter is a true circle for profile cutting. The star and circular text are separate layers so you can assign different operations — pocket, V-carve, or engraving — independently in your CAM software.

## Try This Prompt

Paste this into Claude Code to build this model from scratch:

> Make me a round drink coaster for CNC routing or laser cutting. 3.5 inches across. I want the perimeter as a profile-cut circle, a 5-pointed star outline in the center for pocket or V-carve, and the text "IT'S 5PM SOMEWHERE" in Oswald Bold going around the bottom edge for engraving. Export a single DXF file with three layers: PERIMETER for the outer circle, STAR for the star outline, and TEXT for the character paths.

## Dimensions

| Parameter | Value |
|---|---|
| Diameter | 88.9 mm (3.5") |
| Star outer radius | 14 mm |
| Star inner radius | 6 mm |
| Star points | 5 |
| Text font size | 5.5 mm |
| Text arc radius | ~36.5 mm (2 mm margin from edge) |

## Run

```bash
uv run python projects/cnc-coasters/model.py
```

No arguments — all parameters are at the top of `model.py`.

## Customization

Edit these variables in `model.py`:

| Variable | Default | Description |
|---|---|---|
| `diameter` | `inches_to_mm(3.5)` | Overall coaster diameter |
| `star_outer_r` | `14.0` | Star tip radius (mm) |
| `star_inner_r` | `6.0` | Star valley radius (mm) |
| `text_font_size` | `5.5` | Character height (mm) |
| `text_margin` | `2.0` | Gap from edge to character outer edge (mm) |
| `TEXT` | `"IT'S 5PM SOMEWHERE"` | Circular text string |

## CNC Settings

| Layer | Color | Suggested operation |
|---|---|---|
| `PERIMETER` | Red | Profile/contour cut — cut disc from stock |
| `STAR` | Green | Pocket or V-carve |
| `TEXT` | Blue | V-carve or engraving |

Minimum interior text feature ≈ 1.5 mm — use a ≤ 1/16" bit for text detail work.

## CAM Workflow

Import `cnc-coasters.dxf` into your CAM software and assign toolpaths by layer:

1. **PERIMETER** — profile cut (last operation, or use tabs to hold disc in stock)
2. **STAR** — pocket or V-carve at desired depth
3. **TEXT** — V-carve or fine engraving pass

The perimeter is a native DXF `CIRCLE` entity (exact arc). Star and text are `LWPOLYLINE` — recognized by Vectric, Fusion 360, Carbide Create, LightBurn, and most other CAM tools.

## Files

- `model.py` — parametric source
- `exports/cnc-coasters.dxf` — three-layer vector file
