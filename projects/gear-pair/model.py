"""
Project: Gear Pair — 24-tooth gear + 12-tooth pinion (2:1 ratio)
Description: Two mating involute spur gears, both module 2 / 20° PA.
             Preview shows them meshed at correct center distance.
             Export each gear separately at origin for printing.
Units: mm
Fabrication: FDM or visualization
Colors: 1 per gear — steelblue large gear, coral pinion
"""

import math
from pathlib import Path

from build123d import (
    BuildPart, BuildSketch, Circle, Color, Edge, Mode, Plane,
    Pos, Rot, Vector, Wire, add, extrude, make_face,
)
from ocp_vscode import show

from lib.helpers import check_build_volume, export_multicolor

EXPORT_DIR = Path(__file__).parent / "exports"

# === Shared Gear Parameters ===
MODULE         = 2.0    # tooth size — must be equal between mating gears
PRESSURE_ANGLE = 20.0   # degrees (standard)
THICKNESS      = 10.0   # gear face width (mm)
BORE_DIA       = 5.0    # center bore diameter (mm) — same shaft fits both
N_INV_PTS      = 8      # spline control points per involute flank

# === Individual Gear Parameters ===
N_GEAR   = 24     # large gear teeth
N_PINION = 12     # pinion teeth → 2:1 ratio

# === Print Settings ===
# Orientation: flat face on bed
# Supports: none required
# Layer height: 0.15 mm for clean tooth surfaces
# Print each gear's STLs separately

# ──────────────────────────────────────────────────────────────
# Gear builder
# ──────────────────────────────────────────────────────────────

def _build_gear(n_teeth, color):
    """
    Build one involute spur gear (MODULE / PRESSURE_ANGLE / THICKNESS globals).
    Returns (gear, pitch_radius).
    """
    pitch_r    = MODULE * n_teeth / 2
    base_r     = pitch_r * math.cos(math.radians(PRESSURE_ANGLE))
    tip_r      = pitch_r + MODULE
    root_r     = pitch_r - 1.25 * MODULE   # dedendum circle
    bore_r     = BORE_DIA / 2
    tooth_step = 2 * math.pi / n_teeth

    # ── Involute helpers ──────────────────────────────────────
    def _inv(t, rb):
        return (rb * (math.cos(t) + t * math.sin(t)),
                rb * (math.sin(t) - t * math.cos(t)))

    def _t_for_r(r, rb):
        return math.sqrt(max(0.0, (r / rb) ** 2 - 1))

    def _rot2d(x, y, a):
        c, s = math.cos(a), math.sin(a)
        return x * c - y * s, x * s + y * c

    # ── One tooth's flanks (CW involute: negate y so teeth narrow at tip) ──
    t1 = _t_for_r(tip_r, base_r)
    ip = _inv(_t_for_r(pitch_r, base_r), base_r)
    offset = math.pi / (2 * n_teeth) + math.atan2(ip[1], ip[0])

    right_flank = [
        _rot2d(_inv(t1 * i / (N_INV_PTS - 1), base_r)[0],
               -_inv(t1 * i / (N_INV_PTS - 1), base_r)[1],
               offset)
        for i in range(N_INV_PTS)
    ]
    left_flank = [(x, -y) for x, y in right_flank[::-1]]
    right_3d   = [Vector(x, y, 0) for x, y in right_flank]
    left_3d    = [Vector(x, y, 0) for x, y in left_flank]

    # ── Root step-down points (same angle as base_r endpoints, scaled to root_r) ──
    s = root_r / base_r
    root_right = Vector(right_3d[0].X * s, right_3d[0].Y * s, 0)  # +offset, root_r
    root_left  = Vector(left_3d[-1].X * s, left_3d[-1].Y * s, 0)  # -offset, root_r
    root_mid   = Vector(root_r, 0, 0)                               # angle 0°, root_r

    # ── Tooth 2D face ─────────────────────────────────────────────
    tooth_wire = Wire([
        Edge.make_spline(right_3d),
        Edge.make_three_point_arc(right_3d[-1], Vector(tip_r, 0, 0), left_3d[0]),
        Edge.make_spline(left_3d),
        Edge.make_line(left_3d[-1], root_left),
        Edge.make_three_point_arc(root_left, root_mid, root_right),
        Edge.make_line(root_right, right_3d[0]),
    ])
    tooth_face = make_face(tooth_wire)

    # ── Single 2D sketch → one extrusion → no internal seam edges ─
    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            Circle(root_r)
            for k in range(n_teeth):
                add(Rot(0, 0, math.degrees(k * tooth_step)) * tooth_face)
            Circle(bore_r, mode=Mode.SUBTRACT)
        extrude(amount=THICKNESS)
    gear = bp.part
    gear.color = color
    gear.label = "gear"

    return gear, pitch_r


# ──────────────────────────────────────────────────────────────
# Build both gears
# ──────────────────────────────────────────────────────────────
print("Building gear (24t)...")
gear_body, pr_gear = _build_gear(N_GEAR,   Color("steelblue"))

print("Building pinion (12t)...")
p_body,    pr_pin  = _build_gear(N_PINION, Color("coral"))

# ──────────────────────────────────────────────────────────────
# Mesh position
# ──────────────────────────────────────────────────────────────
center_dist = pr_gear + pr_pin                  # 24 + 12 = 36 mm
# Rotate pinion by half a tooth-pitch so a tooth SPACE faces the gear
mesh_rot    = math.degrees(math.pi / N_PINION)  # 180° / 12 = 15°

def _place_pinion(body):
    return Pos(center_dist, 0, 0) * Rot(0, 0, mesh_rot) * body

# ──────────────────────────────────────────────────────────────
# Display — both gears shown in mesh position
# ──────────────────────────────────────────────────────────────
show(gear_body, _place_pinion(p_body))

# ──────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────
check_build_volume(gear_body)
check_build_volume(p_body)

# ──────────────────────────────────────────────────────────────
# Export — each gear at its own origin, ready to print separately
# ──────────────────────────────────────────────────────────────
export_multicolor([gear_body], "gear-24t",   output_dir=str(EXPORT_DIR))
export_multicolor([p_body],    "pinion-12t", output_dir=str(EXPORT_DIR))
