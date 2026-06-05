"""
Project: cnc-coasters
Description: US flag coaster — 2D vector outlines for CNC routing/engraving.
             Three DXF layers: PERIMETER (profile cut), STAR (pocket/V-carve),
             TEXT (V-carve/engraving).
Units: mm
Fabrication: CNC router or laser cutter
Output: exports/cnc-coasters.dxf
"""

import math
from pathlib import Path

import ezdxf
from build123d import Align, Circle, Plane, Polygon, Text
from ocp_vscode import show

from lib.helpers import FONTS_DIR, inches_to_mm

# === Parameters ===
diameter = inches_to_mm(3.5)            # 3.5" = 88.9 mm
radius   = diameter / 2                 # 44.45 mm

star_outer_r  = 14.0                    # mm — tip-to-center
star_inner_r  =  6.0                    # mm — valley-to-center
star_n_points =  5

TEXT             = "IT'S 5PM SOMEWHERE"
FONT             = str(FONTS_DIR / "Oswald-Bold.ttf")
text_font_size   = 5.5                  # mm
text_margin      = 2.0                  # mm — coaster edge to char outer edge
text_radius      = radius - text_margin - text_font_size / 2
text_char_gap    = 1.2                  # mm — gap between characters
text_center_angle = 270.0              # degrees — arc centered at bottom

# === CNC Settings ===
# PERIMETER — profile/contour cut: cut disc from stock
# STAR      — pocket or V-carve
# TEXT      — V-carve or engraving (min interior feature ≈ 1.5 mm; use ≤ 1/16" bit)
# All dimensions in mm.

EXPORT_DIR = Path(__file__).parent / "exports"


# === Geometry helpers ===

def _star_verts(outer_r: float, inner_r: float, n: int) -> list[tuple[float, float]]:
    verts = []
    for i in range(n * 2):
        ang = math.pi / 2 + i * math.pi / n
        r = outer_r if i % 2 == 0 else inner_r
        verts.append((r * math.cos(ang), r * math.sin(ang)))
    return verts


def _char_faces(text: str, font: str, font_size: float, t_r: float,
                center_angle: float = 270.0, char_gap_mm: float = 1.0) -> list:
    """2D Face objects for each non-space character positioned along an arc."""
    widths = []
    for ch in text:
        if ch == " ":
            widths.append(font_size * 0.38)
        else:
            widths.append(
                Text(ch, font_size=font_size, font_path=font,
                     align=(Align.CENTER, Align.CENTER)).bounding_box().size.X
            )
    char_arcs = [math.degrees(w / t_r) for w in widths]
    gap_arc   = math.degrees(char_gap_mm / t_r)
    total_arc = sum(char_arcs) + gap_arc * (len(text) - 1)
    current   = center_angle - total_arc / 2.0

    faces = []
    for ch, arc in zip(text, char_arcs):
        char_center = current + arc / 2.0
        if ch != " ":
            rad = math.radians(char_center)
            cx, cy = t_r * math.cos(rad), t_r * math.sin(rad)
            tx, ty = -math.sin(rad), math.cos(rad)
            pln = Plane(origin=(cx, cy, 0), x_dir=(tx, ty, 0), z_dir=(0, 0, 1))
            char_shape = pln * Text(ch, font_size=font_size, font_path=font,
                                    align=(Align.CENTER, Align.CENTER))
            try:
                faces.extend(char_shape.faces())
            except AttributeError:
                faces.append(char_shape)
        current += arc + gap_arc
    return faces


# === Model ===

star_verts   = _star_verts(star_outer_r, star_inner_r, star_n_points)
coaster_face = Plane.XY * Circle(radius)
star_face    = Plane.XY * Polygon(*star_verts)
char_faces   = _char_faces(TEXT, FONT, text_font_size, text_radius,
                            center_angle=text_center_angle, char_gap_mm=text_char_gap)

# === Display ===
show(coaster_face, star_face, *char_faces)


# === Export ===

def _discretize_wire(wire, n: int = 32) -> list[tuple[float, float]]:
    """Sample n points per edge along a wire — handles arcs and splines."""
    edges = list(wire.edges())
    if not edges:
        return []
    ordered = [edges.pop(0)]
    while edges:
        tail = ordered[-1].end_point()
        for i, e in enumerate(edges):
            if (tail - e.start_point()).length < 1e-4:
                ordered.append(edges.pop(i))
                break
            if (tail - e.end_point()).length < 1e-4:
                ordered.append(edges.pop(i).reverse())
                break
        else:
            break
    pts = []
    for edge in ordered:
        for j in range(n):
            p = edge.position_at(j / n)
            pts.append((p.X, p.Y))
    return pts


def _add_face_wires(msp, face, layer: str) -> None:
    """Write outer + inner wire contours of a face as closed LWPOLYLINE entities."""
    pts = _discretize_wire(face.outer_wire())
    if len(pts) >= 2:
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    for inner in face.inner_wires():
        pts = _discretize_wire(inner)
        if len(pts) >= 2:
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def export_cnc_dxf(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.new("AC1027")
    doc.header["$INSUNITS"] = 4         # mm
    doc.layers.add("PERIMETER", color=1)    # red
    doc.layers.add("STAR",      color=3)    # green
    doc.layers.add("TEXT",      color=5)    # blue
    msp = doc.modelspace()

    # Perimeter: exact DXF circle entity (not discretized)
    msp.add_circle((0.0, 0.0), radius, dxfattribs={"layer": "PERIMETER"})

    # Star: straight edges — polygon vertices directly, no discretization needed
    msp.add_lwpolyline(star_verts, close=True, dxfattribs={"layer": "STAR"})

    # Text characters: curved glyph outlines discretized to polyline points
    for face in char_faces:
        _add_face_wires(msp, face, "TEXT")

    path = output_dir / "cnc-coasters.dxf"
    doc.saveas(str(path))
    print(f"✓ Exported {path}")


export_cnc_dxf(EXPORT_DIR)
