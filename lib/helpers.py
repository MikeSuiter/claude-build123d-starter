"""Shared helpers for build123d projects."""

from __future__ import annotations

import warnings
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from build123d import (
    Align,
    Compound,
    Mesher,
    Solid,
    export_step,
    export_stl,
    import_svg,
)


def save_preview(path: str) -> None:
    """Save an ISO-view screenshot via ocp_vscode, then restore the original camera."""
    import time

    try:
        from ocp_vscode import Camera, save_screenshot, set_viewer_config, status

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            viewer_status = status()

        if "ambient_intensity" not in viewer_status:
            print("ℹ  Preview skipped — ocp_vscode viewer not running")
            return

        orig = {
            k: viewer_status[k]
            for k in ("position", "quaternion", "target", "zoom")
            if k in viewer_status
        }

        set_viewer_config(reset_camera=Camera.ISO)
        time.sleep(0.5)
        save_screenshot(path)
        time.sleep(0.1)

        if orig:
            set_viewer_config(**orig)

    except ImportError:
        print("ℹ  Preview skipped — ocp_vscode not installed")


FONTS_DIR = Path(__file__).parent.parent / "fonts"

# === Interactive Prompt ===


def ask(prompt: str, default: str = "") -> str:
    """Interactive prompt with default; returns default when stdin is not a tty."""
    import sys

    if not sys.stdin.isatty():
        return default
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw if raw else default


# === Unit Conversion ===


def inches_to_mm(inches: float) -> float:
    """Convert inches to millimeters."""
    return inches * 25.4


# === Build Volume Check ===

# Set this to your machine's work envelope (X, Y, Z in mm) — printer bed, CNC travel, or laser bed.
# Examples: Bambu Lab P2S = (256, 256, 256), Ender 3 = (235, 235, 250), Prusa MK4 = (250, 210, 220)
BUILD_VOLUME: tuple[float, float, float] | None = None


def check_build_volume(
    part: Solid | Compound,
    volume: tuple[float, float, float] | None = None,
) -> bool:
    """Check if a part fits within the machine work envelope (printer bed, CNC travel, or laser bed).

    Set BUILD_VOLUME above for your machine, or pass volume=(X, Y, Z) directly.
    Prints a reminder and returns True if no volume is configured.
    """
    v = volume or BUILD_VOLUME
    if v is None:
        print("ℹ  Build volume not configured — set BUILD_VOLUME in lib/helpers.py")
        return True
    bb = part.bounding_box()
    size = (bb.size.X, bb.size.Y, bb.size.Z)
    for dim, limit, label in zip(size, v, ("X", "Y", "Z")):
        if dim > limit:
            raise ValueError(
                f"Part {label} dimension ({dim:.1f}mm) exceeds build volume ({limit}mm)"
            )
    print(f"✓ Part fits: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")
    return True


# === Export Helpers ===


def _ensure_dir(output_dir: str) -> Path:
    """Create output directory if it doesn't exist."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def export_all(
    part: Solid | Compound,
    name: str,
    output_dir: str = "exports",
) -> None:
    """Export a single-color part as STL + STEP + preview screenshot."""
    d = _ensure_dir(output_dir)
    export_stl(part, str(d / f"{name}.stl"))
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Unknown Compound type")
        export_step(part, str(d / f"{name}.step"))
    save_preview(str(d / f"{name}_preview.png"))
    print(f"✓ Exported {name}.stl and {name}.step to {output_dir}/")


def export_3mf(
    bodies: list[Solid],
    name: str,
    output_dir: str = "exports",
) -> None:
    """Export bodies as 3MF via Mesher, patched to preserve body names/labels.

    Uses Mesher for reliable tessellation, then patches the 3MF XML
    to inject object names so slicers show friendly part names.
    """
    d = _ensure_dir(output_dir)
    filepath = str(d / f"{name}.3mf")

    exporter = Mesher()
    for body in bodies:
        exporter.add_shape(body)
    exporter.write(filepath)

    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"

    with zipfile.ZipFile(filepath, "r") as zin:
        archive_contents = {item: zin.read(item) for item in zin.namelist()}

    ET.register_namespace("", ns)
    ET.register_namespace("p", "http://schemas.microsoft.com/3dmanufacturing/production/2015/06")

    root = ET.fromstring(archive_contents["3D/3dmodel.model"])
    resources = root.find(f"{{{ns}}}resources")

    mesh_objects = [
        obj
        for obj in resources.findall(f"{{{ns}}}object")
        if obj.get("type") == "model" and obj.find(f"{{{ns}}}mesh") is not None
    ]

    for i, obj in enumerate(mesh_objects):
        if i < len(bodies):
            label = bodies[i].label if bodies[i].label else f"body_{i}"
            obj.set("name", label)

    archive_contents["3D/3dmodel.model"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zout:
        for item_name, data in archive_contents.items():
            zout.writestr(item_name, data)

    print(f"✓ Exported {name}.3mf (labeled) to {output_dir}/")


def export_multicolor(
    bodies: list[Solid | Compound],
    name: str,
    output_dir: str = "exports",
) -> None:
    """Export multi-color model as individual STLs + STEP.

    - Individual STLs: one per body, named <name>_<label>.stl
    - STEP: archival format with all bodies as a compound
    """
    d = _ensure_dir(output_dir)

    for body in bodies:
        label = body.label if body.label else "part"
        export_stl(body, str(d / f"{name}_{label}.stl"))
    print(f"✓ Exported {len(bodies)} individual STLs to {output_dir}/")

    compound = Compound(children=bodies)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Unknown Compound type")
        export_step(compound, str(d / f"{name}.step"))
    save_preview(str(d / f"{name}_preview.png"))
    print(f"✓ Exported {name}.step (archival) to {output_dir}/")


def export_dxf_panel(
    face_or_sketch,
    name: str,
    output_dir: str = "exports",
) -> None:
    """Export a 2D face/sketch as DXF with closed LWPOLYLINE entities.

    ExportDXF emits one LINE per edge, which CAM tools like Vectric treat as
    disconnected geometry. This helper uses ezdxf directly to write each wire
    as a single closed LWPOLYLINE, which CAM software can use immediately.
    Supports profiles with inner wires (holes/pockets) as separate polylines.
    """
    import ezdxf

    d = _ensure_dir(output_dir)
    doc = ezdxf.new("AC1027")      # DXF 2013
    doc.header["$INSUNITS"] = 4    # 4 = millimeters
    msp = doc.modelspace()

    try:
        faces = face_or_sketch.faces()
    except AttributeError:
        faces = [face_or_sketch]

    for face in faces:
        _add_wire_as_lwpoly(msp, face.outer_wire())
        for inner in face.inner_wires():
            _add_wire_as_lwpoly(msp, inner)

    doc.saveas(str(d / f"{name}.dxf"))
    print(f"  DXF → {d / f'{name}.dxf'}")


def _add_wire_as_lwpoly(msp, wire) -> None:
    """Trace a closed Wire's edges and add as a single closed LWPOLYLINE."""
    # Build an ordered point list by sorting edges into a connected chain.
    raw_edges = list(wire.edges())
    if not raw_edges:
        return

    ordered = [raw_edges.pop(0)]
    while raw_edges:
        tail = ordered[-1].end_point()
        for i, e in enumerate(raw_edges):
            if (tail - e.start_point()).length < 1e-4:
                ordered.append(raw_edges.pop(i))
                break
            if (tail - e.end_point()).length < 1e-4:
                ordered.append(raw_edges.pop(i).reverse())
                break
        else:
            break  # gap in wire — shouldn't happen for a closed BuildSketch face

    pts = [(e.start_point().X, e.start_point().Y) for e in ordered]
    msp.add_lwpolyline(pts, close=True)


# === SVG Import Helpers ===


def import_svg_faces(
    svg_path: str,
    align: Align | tuple[Align, Align] | None = None,
) -> list:
    """Import SVG and return all paths as Faces/Wires.

    Uses align=None by default to preserve SVG coordinate positions
    (avoids the centering issue caused by the default Align.MIN).
    """
    shapes = import_svg(svg_path, align=align)
    print(f"✓ Imported {len(shapes)} paths from {svg_path}")
    return shapes
