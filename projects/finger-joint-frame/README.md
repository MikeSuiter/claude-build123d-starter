# Finger Joint Box Frame

Open 4-panel frame (no bottom, no lid) with box/finger joints at all four corners.
Cut from 3/4" hardwood on a CNC router. Each panel pair shares a DXF file.

## Dimensions

| Parameter       | Value       |
|-----------------|-------------|
| External length | 203.2 mm (8") |
| External width  | 152.4 mm (6") |
| Panel height    | 101.6 mm (4") |
| Stock thickness | 19.05 mm (3/4") |

## Finger joint details

| Parameter      | Value  |
|----------------|--------|
| Fingers per end (front/back) | 3 |
| Slots per end (left/right)   | 3 |
| Finger/slot width            | 20.32 mm |
| Slot depth                   | 19.05 mm (= stock thickness) |

## Run

```bash
uv run python projects/finger-joint-frame/model.py
```

## Exports

| File | Use |
|------|-----|
| `exports/front_back.dxf` | CNC profile for 2 long panels (8") |
| `exports/left_right.dxf` | CNC profile for 2 short panels (6") |
| `exports/finger-joint-frame.step` | 3D assembly reference |

Cut 2 copies of each DXF. No kerf compensation included — add ~0.1–0.15 mm outward
offset in your CAM software for a snug fit.

## Fabrication

| Setting   | Value              |
|-----------|--------------------|
| Method    | CNC router         |
| Material  | 3/4" hardwood      |
| Toolpaths | 2D contour/profile |
| Notes     | Climb-cut outer profile; conventional-cut pockets for slots. Tabs recommended to hold parts during cut. |
