Create a new build123d project.

1. Ask the user what they want to model
2. Ask the essential questions from CLAUDE.md (skip anything already answered):
   - Overall dimensions and units
   - Fabrication method (FDM, SLA, CNC, laser, reference)
   - For 3D printing: printer make/model and build volume
   - Number of colors/materials (and which parts get which color)
   - Any mating or fit surfaces (press fit, slip fit, clearance)
   - Material (PLA, PETG, wood, aluminum, etc.)
3. **Ask if the design includes any logos, text, or SVG graphics to import.**
   If yes, ask the user to provide the SVG file(s) and review them before modeling:
   - Import with `align=None` to preserve coordinates
   - Verify ALL paths imported successfully — never drop paths
   - Plan how the SVG will be positioned on the model (which face, scale, extrude/cut)
4. Plan the modeling approach:
   - Sketch-first strategy and operation order
   - Color/body separation for multi-color prints
   - SVG placement strategy if applicable
5. Copy projects/_template/ to projects/<project-name>/
6. Create the README.md with the project description and parameters
7. Implement the model in model.py following the incremental workflow:
   base geometry → features one at a time → color separation → export
8. Run `uv run python projects/<project-name>/model.py` to verify it works
9. Export using `export_all()` (single-color) or `export_multicolor()` (multi-color)
