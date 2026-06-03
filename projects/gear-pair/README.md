# Gear Pair — Involute Spur Gears

Two meshing involute spur gears (24-tooth gear + 12-tooth pinion, 2:1 ratio).
The preview shows them positioned at correct center distance. Each gear exports
separately so you can print or use them independently.

Tooth flanks are smooth B-spline curves through involute sample points — not polygon
approximations. Change `MODULE` and tooth counts; everything recomputes automatically.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `MODULE` | 2.0 mm | Tooth size. Both gears must share the same module to mesh. |
| `PRESSURE_ANGLE` | 20° | Standard involute pressure angle. Don't change unless you know why. |
| `THICKNESS` | 10.0 mm | Gear face width (depth front-to-back). |
| `BORE_DIA` | 5.0 mm | Center bore diameter. Same for both gears — one shaft fits both. |
| `N_GEAR` | 24 | Tooth count on the large gear. |
| `N_PINION` | 12 | Tooth count on the pinion. Ratio = N_GEAR / N_PINION = 2:1. |
| `N_INV_PTS` | 8 | Spline control points per tooth flank. 8 is smooth; raise for closer-to-perfect. |

## Derived Geometry (at defaults)

| Quantity | Large Gear | Pinion |
|---|---|---|
| Pitch diameter | 48.0 mm | 24.0 mm |
| Tip diameter | 52.0 mm | 28.0 mm |
| Root diameter | 43.0 mm | 19.0 mm |
| Center distance | — | 36.0 mm (sum of pitch radii) |

## Run

```bash
uv run python projects/gear-pair/model.py
```

The OCP CAD Viewer shows both gears meshed at their operating center distance.
Large gear is steel blue; pinion is coral.

## Exports

Files are written to `projects/gear-pair/exports/`:

| File | Use |
|---|---|
| `gear-24t_gear.stl` | Large gear — import into slicer |
| `gear-24t.step` | Large gear — archival / CAD import |
| `pinion-12t_gear.stl` | Pinion — import into slicer |
| `pinion-12t.step` | Pinion — archival / CAD import |

Each gear is exported at the origin (not in the meshed position), so you can
slice or use them independently without repositioning.

## Fabrication

| Setting | Value |
|---|---|
| Method | FDM 3D print or reference visualization |
| Material | PLA or PETG |
| Orientation | Flat face on bed (teeth pointing up) |
| Supports | None required |
| Layer height | 0.15 mm for clean tooth surfaces |
| Infill | 40%+ for functional gears; 15% for display |

For functional gears: PETG is more durable than PLA. The bore is exactly `BORE_DIA`;
add 0.2–0.3 mm to `BORE_DIA` if you need a slip fit over a real shaft.

## Gear Math (brief)

An involute gear tooth flank follows the curve unrolled from the base circle:

```
x = r_b · (cos t + t·sin t)
y = r_b · (sin t − t·cos t)
```

where `r_b = pitch_r · cos(pressure_angle)` is the base circle radius and `t` is
the involute parameter (0 at base circle, larger toward tip).

Key circles:
- **Pitch circle** (`MODULE × N / 2`): the "rolling" circle — where two meshing gears
  make contact on the pitch line
- **Base circle**: where the involute starts — tooth flank below this is a straight radial fillet
- **Tip circle** (`pitch_r + MODULE`): outer edge of tooth
- **Root circle** (`pitch_r − 1.25 × MODULE`): bottom of tooth space

Two gears mesh correctly when their modules and pressure angles match and their center
distance equals the sum of their pitch radii.
