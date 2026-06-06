"""
Project: Mountain Range Relief
Description: Smooth 3D mountain range for CNC 3D contouring. Import STEP into VCarve.
Units: mm (8" × 5" × 1.5" stock)
"""

from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from build123d import Edge, Vector, Wire, loft, make_face
from ocp_vscode import show

from lib.helpers import export_all

# === Parameters ===
WIDTH      = 203.2  # 8 inches
DEPTH      = 127.0  # 5 inches
BASE_H     =  12.7  # 0.5" flat base thickness
MAX_RELIEF =  25.4  # 1" max mountain height above base
N_SECTIONS =  20    # loft cross-sections (increase for smoother result)
N_PTS_Y    =  18    # Y sample points per cross-section (including endpoints)

# Gaussian peaks: (x_center_mm, y_center_mm, amplitude_mm, sigma_x_mm, sigma_y_mm)
# Peaks are offset in Y for naturalistic, non-symmetric ridgeline
PEAKS = [
    (-70, -12, 19, 28, 18),   # far-left, low
    (-25,  10, 32, 22, 18),   # left-center, tallest
    ( 28, -15, 26, 20, 18),   # right-center
    ( 72,   8, 16, 18, 16),   # far-right, smallest
]

# === CNC Settings ===
# Stock: 8" × 5" × 1.5" (203.2 × 127 × 38.1 mm)
# Material: hardwood, MDF, or similar
# Max relief: 25.4mm (1") above 12.7mm (0.5") flat base
# Import mountain-range.step into VCarve for 3D contouring toolpath

# === Model ===

def terrain_h(x: float, y: float) -> float:
    """Height above base at (x, y) — sum of 2D Gaussian bumps."""
    h = 0.0
    for cx, cy, amp, sx, sy in PEAKS:
        h += amp * math.exp(-((x - cx) ** 2 / (2 * sx ** 2) + (y - cy) ** 2 / (2 * sy ** 2)))
    return min(h, MAX_RELIEF)


def make_cross_section(x_i: float):
    """Closed face at x=x_i: terrain spline on top, flat base edge on bottom."""
    y_start = -DEPTH / 2
    y_end   =  DEPTH / 2

    y_samples = [y_start + j * DEPTH / (N_PTS_Y - 1) for j in range(N_PTS_Y)]

    # Spline endpoints pinned to BASE_H; interior follows terrain function
    spline_pts = [Vector(x_i, y_start, BASE_H)]
    for y_j in y_samples[1:-1]:
        spline_pts.append(Vector(x_i, y_j, BASE_H + terrain_h(x_i, y_j)))
    spline_pts.append(Vector(x_i, y_end, BASE_H))

    terrain_edge = Edge.make_spline(spline_pts)
    base_edge    = Edge.make_line(
        Vector(x_i, y_end, BASE_H),
        Vector(x_i, y_start, BASE_H),
    )

    return make_face(Wire([terrain_edge, base_edge]))


print("Building cross-sections...")
sections = []
for i in range(N_SECTIONS):
    x_i = -WIDTH / 2 + i * WIDTH / (N_SECTIONS - 1)
    sections.append(make_cross_section(x_i))
    if (i + 1) % 5 == 0:
        print(f"  {i + 1}/{N_SECTIONS}")

print("Lofting...")
mountain = loft(sections)

# === Display ===
show(mountain)

# === Validation ===
bb = mountain.bounding_box()
print(f"Bounding box: {bb.size.X:.1f} × {bb.size.Y:.1f} × {bb.size.Z:.1f} mm")

# === Export ===
EXPORT_DIR = Path(__file__).parent / "exports"
export_all(mountain, "mountain-range", output_dir=str(EXPORT_DIR))
