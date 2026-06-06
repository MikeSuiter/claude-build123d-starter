# Mountain Range Relief

Smooth 3D mountain range carved as a continuous surface — no layered terracing. Four Gaussian peaks of varying heights and widths, offset in Y for a natural asymmetric ridgeline. Designed for 3D contouring on a CNC router; import the STEP into VCarve and let it generate the toolpaths.

## Try This Prompt

Paste this into Claude Code to build this model from scratch:

> I want a smooth 3D mountain range relief for CNC routing. 8 inches wide by 5 inches deep, fits in 1.5" stock. I want 4 peaks of different heights blending smoothly into each other — no sharp layers, just a natural flowing terrain like a real mountain range. Export a STEP file so I can import it into VCarve for 3D contouring toolpaths.

## Dimensions

| Parameter | Value |
|---|---|
| Width | 203.2 mm (8") |
| Depth | 127.0 mm (5") |
| Base thickness | 12.7 mm (0.5") |
| Max relief height | 25.4 mm (1") |
| Total stock height | 38.1 mm (1.5") |
| Peaks | 4 (parametric) |

## Run

```bash
uv run python projects/mountain-range/model.py
```

## Customization

Edit these variables in `model.py`:

| Variable | Default | Description |
|---|---|---|
| `WIDTH` | `203.2` | Overall width (mm) |
| `DEPTH` | `127.0` | Overall depth (mm) |
| `BASE_H` | `12.7` | Flat base thickness below terrain (mm) |
| `MAX_RELIEF` | `25.4` | Max mountain height above base (mm) |
| `N_SECTIONS` | `20` | Loft cross-sections — increase for smoother surface |
| `PEAKS` | 4-entry list | Each peak: `(x, y, amplitude, sigma_x, sigma_y)` in mm |

To add, remove, or reshape peaks, edit the `PEAKS` list. `sigma_x` / `sigma_y` control how wide each peak spreads in each direction — larger values make broader, rounder mountains.

## Fabrication

| Setting | Value |
|---|---|
| Method | CNC router — 3D contouring |
| Stock | 8" × 5" × 1.5" hardwood, MDF, or similar |
| Toolpath | 3D raster or parallel finishing pass in VCarve |
| Bit | Any ball-nose end mill; 1/4" for roughing, 1/8" for finishing |
| Notes | No dogbone corners or 2D profiles — pure 3D surface |

## CAM Workflow

1. Import `exports/mountain-range.step` into VCarve Pro (or similar)
2. Set material size to match stock: 203.2 × 127.0 × 38.1 mm
3. Create a **3D Roughing** toolpath (large ball-nose, e.g. 1/4") to remove bulk material
4. Create a **3D Finishing** toolpath (small ball-nose, e.g. 1/8", 10–15% stepover) for the smooth surface
5. Run roughing first, then finishing

A tighter stepover on the finishing pass gives a smoother surface that requires less hand-sanding.

## Files

| File | Use |
|---|---|
| `model.py` | Parametric source |
| `exports/mountain-range.step` | Import into VCarve for 3D toolpaths |
| `exports/mountain-range.stl` | Mesh reference / alternative CAM import |
