"""
Project: color-coaster
Description: US flag coaster — white star center, blue/red half-rings,
             white underside, solid white circular text flush with top face
Units: mm
Printer: Any multi-material FDM printer
Colors: 3 — white (star + base + text), blue (top half), red (bottom half)
Print orientation: decorative face UP; flip in slicer for printing
"""

import math
from pathlib import Path

from build123d import (
    Align, Axis, Box, Color, Compound, Cylinder,
    GeomType, Plane, Polygon, Pos, Text, chamfer, extrude,
)
from ocp_vscode import show

from lib.helpers import (
    FONTS_DIR,
    check_build_volume,
    export_multicolor,
    inches_to_mm,
)

# === Parameters ===
diameter = inches_to_mm(3.5)        # 3.5" = 88.9 mm
radius = diameter / 2               # 44.45 mm
thickness = 4.0                     # mm
chamfer_size = 1.0                  # mm
face_depth = 1.0                    # mm — height of colored face layer

# Star (replaces grey center circle)
star_outer_r = 14.0                 # mm — outer tip radius
star_inner_r = 6.0                  # mm — inner valley radius
star_n_points = 5

# Circular text — flush black inlay, centered at bottom of coaster
TEXT = "MY COOL COASTER"
FONT = str(FONTS_DIR / "Oswald-Bold.ttf")
text_font_size = 5.5                # mm
text_margin = 2.0                   # mm from coaster outer edge to char outer edge
text_inlay_depth = face_depth       # mm — inlay fills full face layer, top flush with coaster surface
text_radius = radius - text_margin - text_font_size / 2  # char center radius
text_char_gap = 1.2                 # mm — gap between characters (no forced kerning to fill circle)
text_center_angle = 270.0           # degrees — arc centered at bottom of coaster

# Colors (parametric — change these to restyle the coaster)
COLOR_WHITE  = Color(1.0,   1.0,   1.0  )  # star, base, text — assign same white material in slicer
COLOR_BLUE   = Color(0.0,   0.157, 0.408)  # US flag navy (Pantone 281 C approx)
COLOR_RED    = Color(0.749, 0.039, 0.188)  # US flag red  (Pantone 193 C approx)

# === Print Settings ===
# Orientation: flip in slicer (decorative face down for clean surface finish)
# Supports: none  |  Nozzle: 0.4mm  |  Layer height: 0.20mm  |  Colors: 5

# === Helpers ===

def _make_star_solid(outer_r: float, inner_r: float, n: int, z: float, h: float):
    """Extrude a star polygon from z upward by h."""
    verts = []
    for i in range(n * 2):
        ang = math.pi / 2 + i * math.pi / n
        r = outer_r if i % 2 == 0 else inner_r
        verts.append((r * math.cos(ang), r * math.sin(ang)))
    star_plane = Plane(origin=(0, 0, z), z_dir=(0, 0, 1))
    star_face = star_plane * Polygon(*verts)
    return extrude(star_face, h)


def _make_text_solids(text: str, font: str, font_size: float, t_r: float,
                      z: float, depth: float, center_angle: float = 270.0,
                      char_gap_mm: float = 1.0):
    """
    Solid inlay per non-space character, arc centered at center_angle (clockwise).
    Uses measured character widths — no forced equal spacing to fill the circle.
    Spaces advance position without creating a solid.
    """
    # Measure each character's advance width
    widths = []
    for ch in text:
        if ch == " ":
            widths.append(font_size * 0.38)   # Oswald space ≈ 38% of em
        else:
            widths.append(
                Text(ch, font_size=font_size, font_path=font,
                     align=(Align.CENTER, Align.CENTER)).bounding_box().size.X
            )

    # Convert mm widths → arc degrees at radius t_r
    char_arcs = [math.degrees(w / t_r) for w in widths]
    gap_arc = math.degrees(char_gap_mm / t_r)
    total_arc = sum(char_arcs) + gap_arc * (len(text) - 1)

    # First char starts at center_angle − half the total arc; sweep CCW (increasing angle)
    # so text reads left-to-right when viewed from the coaster face.
    # CCW tangent (−sin θ, cos θ) keeps character tops pointing toward center.
    current = center_angle - total_arc / 2.0

    bodies = []
    for ch, arc in zip(text, char_arcs):
        char_center = current + arc / 2.0
        if ch != " ":
            rad = math.radians(char_center)
            cx, cy = t_r * math.cos(rad), t_r * math.sin(rad)
            tx, ty = -math.sin(rad), math.cos(rad)   # CCW tangent — upright at bottom arc
            pln = Plane(origin=(cx, cy, z), x_dir=(tx, ty, 0), z_dir=(0, 0, 1))
            sk = pln * Text(ch, font_size=font_size, font_path=font,
                            align=(Align.CENTER, Align.CENTER))
            bodies.append(extrude(sk, amount=-depth))
        current += arc + gap_arc

    return bodies


# === Model ===

# Base cylinder with chamfered top outer edge
coaster = Cylinder(radius, thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
top_edge = coaster.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[-1]
coaster_chamfered = chamfer(top_edge, chamfer_size)

# Face slab: top face_depth mm (where all colors live)
face_slab = Pos(0, 0, thickness) * Box(
    diameter * 2, diameter * 2, face_depth,
    align=(Align.CENTER, Align.CENTER, Align.MAX),
)

# Half-plane cutters for yellow/red split
top_half = Box(diameter * 2, radius * 2, thickness, align=(Align.CENTER, Align.MIN, Align.MIN))
bot_half = Box(diameter * 2, radius * 2, thickness, align=(Align.CENTER, Align.MAX, Align.MIN))

# Orange star (face layer only, clipped to coaster outline)
star_solid = _make_star_solid(star_outer_r, star_inner_r, star_n_points,
                               thickness - face_depth, face_depth)
orange_body = star_solid & coaster_chamfered

# Text: solid inlay bodies (flush with top face, cut pocket into yellow/red)
text_solids = _make_text_solids(
    TEXT, FONT, text_font_size, text_radius,
    thickness, text_inlay_depth,
    center_angle=text_center_angle, char_gap_mm=text_char_gap,
)

# Pocket cutters — remove text volume from yellow/red so inlay fits flush
yellow_body = (coaster_chamfered & top_half & face_slab) - star_solid
red_body    = (coaster_chamfered & bot_half & face_slab) - star_solid
for ts in text_solids:
    yellow_body = yellow_body - ts
    red_body    = red_body    - ts

# Black base (everything below the face layer)
black_body = coaster_chamfered - face_slab

# White body: fuse base + star + all text inlays — one STL, one filament slot
white_body = black_body + orange_body
for ts in text_solids:
    white_body = white_body + ts

# Assign colors and labels
white_body.color  = COLOR_WHITE;  white_body.label  = "white"
yellow_body.color = COLOR_BLUE;   yellow_body.label = "blue"
red_body.color    = COLOR_RED;    red_body.label    = "red"

# === Display ===
show(white_body, yellow_body, red_body)

# === Validation ===
check_build_volume(Compound(children=[white_body, yellow_body, red_body]))

# === Export ===
EXPORT_DIR = str(Path(__file__).parent / "exports")
export_multicolor(
    [white_body, yellow_body, red_body],
    "color-coaster",
    output_dir=EXPORT_DIR,
)
