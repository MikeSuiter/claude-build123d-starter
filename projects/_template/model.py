"""
Project: [PROJECT NAME]
Description: [Brief description]
Units: mm (modeled in mm; original dimensions noted in inches where applicable)
Printer: [Make/Model, build volume]
Colors: 1 (single color — update if multi-color)
"""

from pathlib import Path

# Import only what you need from build123d (avoid wildcard imports)
from build123d import Box
from ocp_vscode import show

from lib.helpers import check_build_volume

# === Parameters ===
# Define all dimensions as variables. Comment original inch values if converted.
length = 100.0  # mm
width = 50.0  # mm
height = 25.0  # mm

# === Print Settings ===
# Orientation: bottom face on bed
# Supports: none required
# Nozzle: 0.4mm
# Layer height: 0.20mm recommended
# Colors/Materials: 1

# === Model ===
part = Box(length, width, height)

# === Display ===
show(part)

# === Validation ===
check_build_volume(part)  # Configure BUILD_VOLUME in lib/helpers.py for your printer

# === Export ===
EXPORT_DIR = str(Path(__file__).parent / "exports")
# from lib.helpers import export_all
# export_all(part, "project-name", output_dir=EXPORT_DIR)

# --- Multi-color alternative (uncomment and adapt) ---
# from build123d import Color
# from lib.helpers import export_multicolor
# body_a.color = Color("black"); body_a.label = "base"
# body_b.color = Color("red");   body_b.label = "accent"
# export_multicolor([body_a, body_b], "project-name", output_dir=EXPORT_DIR)
