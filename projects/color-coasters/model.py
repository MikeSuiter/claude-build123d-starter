"""
Project: color-coaster
Description: 4-color round coaster with grey center, yellow/red half-rings, black underside
Units: mm (modeled in mm; dimensions given in inches converted below)
Printer: Any multi-material FDM printer
Colors: 4 — grey, yellow, red, black
Print orientation: decorative face UP in model, flip in slicer for printing
"""

from pathlib import Path

from build123d import Align, Axis, Box, Color, Cylinder, GeomType, Pos, chamfer
from ocp_vscode import show

from lib.helpers import (
    check_build_volume,
    export_multicolor,
    inches_to_mm,
)

# === Parameters ===
diameter = inches_to_mm(3.5)  # 3.5" = 88.9 mm
radius = diameter / 2  # 44.45 mm
thickness = 4.0  # mm
grey_diameter = inches_to_mm(1.0)  # 1" = 25.4 mm
grey_radius = grey_diameter / 2  # 12.7 mm
chamfer_size = 1.0  # mm (45° chamfer)
face_depth = 1.0  # mm (thickness of colored face regions)

# === Print Settings ===
# Orientation: flip in slicer so decorative face is on textured bed
# Supports: none — flat disc
# Nozzle: 0.4mm
# Layer height: 0.20mm recommended
# Colors/Materials: 4 (grey, yellow, red, black)

# === Model ===

# Full base cylinder — decorative face at top (z=thickness)
coaster = Cylinder(radius, thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))

# Chamfer the top outer edge (decorative side, at z=thickness)
edges = coaster.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)
top_edge = edges[-1]
coaster_chamfered = chamfer(top_edge, chamfer_size)

# --- Color region cutters ---

# Face slab at the top: z=(thickness - face_depth) to z=thickness
face_slab = Pos(0, 0, thickness) * Box(
    diameter * 2,
    diameter * 2,
    face_depth,
    align=(Align.CENTER, Align.CENTER, Align.MAX),
)

# Grey center cutter
grey_cutter = Cylinder(grey_radius, thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))

# Top half: y >= 0
top_half_cutter = Box(
    diameter * 2,
    radius * 2,
    thickness,
    align=(Align.CENTER, Align.MIN, Align.MIN),
)

# Bottom half: y <= 0
bottom_half_cutter = Box(
    diameter * 2,
    radius * 2,
    thickness,
    align=(Align.CENTER, Align.MAX, Align.MIN),
)

# --- Build the four colored bodies ---
grey_body = coaster_chamfered & grey_cutter & face_slab
yellow_body = (coaster_chamfered & top_half_cutter & face_slab) - grey_cutter
red_body = (coaster_chamfered & bottom_half_cutter & face_slab) - grey_cutter
black_body = coaster_chamfered - face_slab

# Assign colors and labels
grey_body.color = Color(0.5, 0.5, 0.5)
grey_body.label = "grey"
yellow_body.color = Color(1.0, 1.0, 0.0)
yellow_body.label = "yellow"
red_body.color = Color(1.0, 0.0, 0.0)
red_body.label = "red"
black_body.color = Color(0.0, 0.0, 0.0)
black_body.label = "black"

# === Display ===
show(grey_body, yellow_body, red_body, black_body)

# === Validation ===
combined = grey_body + yellow_body + red_body + black_body
check_build_volume(combined)

# === Export ===
EXPORT_DIR = str(Path(__file__).parent / "exports")

export_multicolor(
    [grey_body, yellow_body, red_body, black_body],
    "color-coaster",
    output_dir=EXPORT_DIR,
)
