"""Blender (bpy) side of the neuro-cube: build objects from a design, export geometry from objects.

The objects and their custom properties are the source of truth. Physical values
are stored as SI custom properties (double precision); object locations use a
display transform (1 Blender unit = 1 mm; lateral positions exaggerated by
LATERAL_DISPLAY_SCALE so 50 um pitches are visible). The export reads the
properties, never the display coordinates.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for _p in (str(ROOT), str(HERE), "D:/TOOLS/blender_pylibs_neurocubo"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402
import neurocubo_core as nc  # noqa: E402

LATERAL_DISPLAY_SCALE = 20.0
MM = 1000.0
GUIDE_DISPLAY_RADIUS_MM = 0.12


def script_args() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _collection(name: str, parent=None):
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def _empty(name: str, col, location=(0, 0, 0), size=0.5):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = size
    obj.location = location
    col.objects.link(obj)
    return obj


def _box(name: str, col, center, dims):
    mesh = bpy.data.meshes.new(name)
    hx, hy, hz = (d / 2 for d in dims)
    verts = [(sx * hx, sy * hy, sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    col.objects.link(obj)
    return obj


def _curve(name: str, col, points):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = GUIDE_DISPLAY_RADIUS_MM
    data.bevel_resolution = 2
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, (x, y, z) in zip(spline.points, points):
        point.co = (x, y, z, 1.0)
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    return obj


class Display:
    """Physical (m) -> display (mm, exaggerated lateral) transform."""

    def __init__(self, design: dict):
        self.side = design["cube"]["side_m"]
        self.design = design

    def x(self, x_m: float, direction: int) -> float:
        return (x_m if direction > 0 else self.side - x_m) * MM

    def y(self, y_m: float) -> float:
        return y_m * MM * LATERAL_DISPLAY_SCALE

    def z(self, depth_m: float) -> float:
        return -depth_m * MM


def mode_y(layer: dict, mode: int) -> float:
    return (mode - (layer["n"] - 1) / 2) * layer["mode_pitch_m"]


def _sbend(x0, x1, y0, y1, steps=10):
    return [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * (1 - math.cos(math.pi * t)) / 2)
            for t in np.linspace(0, 1, steps)]


def guide_paths(layer: dict, design: dict):
    """Polylines (x_m, y_m) per (mode, column) for drawing; nominal layout only."""
    n = layer["n"]
    margin = design["cube"]["margin_m"]
    col_len = layer["column_path_m"][0]
    paths = {}
    by_col = {}
    for item in layer["mzis"]:
        by_col.setdefault(item["column"], []).append(item)
    for col in range(1, layer["stages"] + 1):
        x0, x1 = margin + (col - 1) * col_len, margin + col * col_len
        busy = {}
        for item in by_col.get(col, []):
            m = item["modes"][0]
            busy[m], busy[m + 1] = (item, +1), (item, -1)
        for mode in range(n):
            y = mode_y(layer, mode)
            if mode not in busy:
                paths[(mode, col)] = [(x0, y), (x1, y)]
                continue
            item, sign = busy[mode]
            centre = (mode_y(layer, item["modes"][0]) + mode_y(layer, item["modes"][1])) / 2
            yc = centre + sign * item["coupler_in"]["gap_m"] / 2
            h = item["heater_phi"]["length_m"]
            sb = (item["coupler_in"]["x_m"] - x0 - h)
            ci, co = item["coupler_in"], item["coupler_out"]
            pts = [(x0, y), (x0 + h, y)]
            pts += _sbend(x0 + h, ci["x_m"], y, yc)[1:]
            pts += [(ci["x_m"] + ci["length_m"], yc)]
            pts += _sbend(ci["x_m"] + ci["length_m"], ci["x_m"] + ci["length_m"] + sb, yc, y)[1:]
            pts += [(co["x_m"] - sb, y)]
            pts += _sbend(co["x_m"] - sb, co["x_m"], y, yc)[1:]
            pts += [(co["x_m"] + co["length_m"], yc)]
            pts += _sbend(co["x_m"] + co["length_m"], x1, yc, y)[1:]
            paths[(mode, col)] = pts
    out_x0 = margin + layer["stages"] * col_len
    for mode in range(n):
        y = mode_y(layer, mode)
        paths[(mode, layer["stages"] + 1)] = [(out_x0, y), (out_x0 + layer["output_section_path_m"], y)]
    return paths


def build(design: dict) -> None:
    """Create every object of the neuro-cube with SI custom properties."""
    disp = Display(design)
    root = _collection("NeuroCube")
    side_mm = design["cube"]["side_m"] * MM
    cube = _box("NC_Cube", root, (side_mm / 2, 0.0, -side_mm / 2), (side_mm, side_mm, side_mm))
    cube["nc_role"] = "cube"
    cube["side_m"] = design["cube"]["side_m"]
    meta = {k: v for k, v in design.items() if k not in ("layers", "optoelectronic_stage", "readout")}
    cube["design_meta_json"] = json.dumps(meta, sort_keys=True)
    cube.display_type = "WIRE"
    for li, layer in enumerate(design["layers"]):
        col = _collection("NC_" + layer["name"], root)
        d = layer["direction"]
        z = disp.z(layer["depth_m"])
        lobj = _empty("NC_%s" % layer["name"], col, (disp.x(0, d), 0, z))
        lobj["nc_role"] = "layer"
        lobj["layer_index"] = li
        for key in ("name", "n", "depth_m", "direction", "stages", "loss_db_per_stage",
                    "mode_pitch_m", "output_section_path_m"):
            lobj[key] = layer[key]
        lobj["column_path_m"] = list(layer["column_path_m"])
        for item in layer["mzis"]:
            k, m = item["index"], item["modes"][0]
            yc = disp.y((mode_y(layer, m) + mode_y(layer, m + 1)) / 2)
            base = "NC_%s_M%02d" % (layer["name"], k)
            e = _empty(base, col, (disp.x(item["x_start_m"], d), yc, z), 0.3)
            e["nc_role"] = "mzi"
            e["layer_index"], e["index"], e["mode"], e["column"] = li, k, m, item["column"]
            e["x_start_m"] = item["x_start_m"]
            e["arm_outer_m"] = list(item["arm_path_m"]["outer"])
            e["arm_inner_m"] = list(item["arm_path_m"]["inner"])
            for role in ("coupler_in", "coupler_out"):
                c = item[role]
                xc = disp.x(c["x_m"] + c["length_m"] / 2, d)
                obj = _box(base + "_" + role, col, (xc, yc, z),
                           (c["length_m"] * MM, disp.y(c["gap_m"]) + 0.4, 0.4))
                obj["nc_role"] = "coupler"
                obj["layer_index"], obj["index"], obj["port"] = li, k, role
                obj["gap_m"], obj["length_m"], obj["x_m"] = c["gap_m"], c["length_m"], c["x_m"]
                obj["kappa_per_m"] = nc.kappa_of_gap(c["gap_m"])
                obj.display_type = "WIRE"
            for role, arm_mode in (("heater_theta", m), ("heater_phi", m)):
                h = item[role]
                xh = disp.x(h["x_m"] + h["length_m"] / 2, d)
                obj = _box(base + "_" + role.split("_")[1], col,
                           (xh, disp.y(mode_y(layer, arm_mode)), z + 0.35),
                           (h["length_m"] * MM, 0.5, 0.12))
                obj["nc_role"] = "heater"
                obj["layer_index"], obj["index"], obj["kind"] = li, k, role.split("_")[1]
                obj["phi"] = float(h["phi"])
                obj["length_m"], obj["x_m"] = h["length_m"], h["x_m"]
        for item in layer["output_heaters"]:
            obj = _box("NC_%s_OUT%d" % (layer["name"], item["mode"]), col,
                       (disp.x(item["x_m"] + item["length_m"] / 2, d), disp.y(mode_y(layer, item["mode"])), z + 0.35),
                       (item["length_m"] * MM, 0.5, 0.12))
            obj["nc_role"] = "heater_out"
            obj["layer_index"], obj["mode"] = li, item["mode"]
            obj["phi"] = float(item["phi"])
            obj["length_m"], obj["x_m"] = item["length_m"], item["x_m"]
        gcol = _collection("NC_%s_guides" % layer["name"], col)
        for (mode, column), pts in guide_paths(layer, design).items():
            obj = _curve("NC_%s_G%d_C%02d" % (layer["name"], mode, column), gcol,
                         [(disp.x(x, d), disp.y(y), z) for x, y in pts])
            obj["nc_role"] = "guide"
            obj["layer_index"], obj["mode"], obj["column"] = li, mode, column
    oe, ro = design["optoelectronic_stage"], design["readout"]
    n = design["layers"][0]["n"]
    ocol = _collection("NC_Optoelectronics", root)
    oobj = _box("NC_OE", ocol, (side_mm + 1.5, 0, (disp.z(design["layers"][0]["depth_m"]) +
                                                   disp.z(design["layers"][1]["depth_m"])) / 2),
                (2.0, disp.y(n * design["layers"][0]["mode_pitch_m"]) + 1, 4.0))
    oobj["nc_role"] = "oe"
    oobj["type"], oobj["v_pi"], oobj["bias"], oobj["note"] = oe["type"], oe["v_pi"], oe["bias"], oe["note"]
    robj = _box("NC_Readout", ocol, (-1.5, 0, disp.z(design["layers"][1]["depth_m"])),
                (2.0, disp.y(n * design["layers"][1]["mode_pitch_m"]) + 1, 1.5))
    robj["nc_role"] = "readout"
    robj["gain"], robj["ports"], robj["note"] = ro["gain"], list(ro["ports"]), ro["note"]
    iobj = _box("NC_Input", ocol, (-1.5, 0, disp.z(design["layers"][0]["depth_m"])),
                (2.0, disp.y(n * design["layers"][0]["mode_pitch_m"]) + 1, 1.5))
    iobj["nc_role"] = "input"
    iobj["encoding"] = design["input_encoding"]


def objects_by_role(role: str):
    return [o for o in bpy.data.objects if o.get("nc_role") == role]


def heater_objects(n_mzi_per_layer: list[int]):
    """Heater objects in parameter order (layer, theta_k, phi_k ..., out_j)."""
    table = {}
    for o in objects_by_role("heater"):
        table[(o["layer_index"], o["index"], o["kind"])] = o
    for o in objects_by_role("heater_out"):
        table[(o["layer_index"], "out", o["mode"])] = o
    ordered = []
    for li, k_count in enumerate(n_mzi_per_layer):
        n = next(o for o in objects_by_role("layer") if o["layer_index"] == li)["n"]
        for k in range(k_count):
            ordered += [table[(li, k, "theta")], table[(li, k, "phi")]]
        ordered += [table[(li, "out", j)] for j in range(n)]
    return ordered


def export_geometry() -> dict:
    """Geometry record rebuilt from object properties only, with its SHA-256."""
    cube = objects_by_role("cube")[0]
    geometry = json.loads(cube["design_meta_json"])
    layers = []
    for lobj in sorted(objects_by_role("layer"), key=lambda o: o["layer_index"]):
        li = lobj["layer_index"]
        layer = {key: lobj[key] for key in ("name", "n", "depth_m", "direction", "stages",
                                            "loss_db_per_stage", "mode_pitch_m", "output_section_path_m")}
        layer["column_path_m"] = [float(v) for v in lobj["column_path_m"]]
        couplers = {(o["index"], o["port"]): o for o in objects_by_role("coupler") if o["layer_index"] == li}
        heaters = {(o["index"], o["kind"]): o for o in objects_by_role("heater") if o["layer_index"] == li}
        mzis = []
        for e in sorted((o for o in objects_by_role("mzi") if o["layer_index"] == li), key=lambda o: o["index"]):
            k = e["index"]
            item = {"index": k, "modes": [e["mode"], e["mode"] + 1], "column": e["column"],
                    "x_start_m": e["x_start_m"],
                    "arm_path_m": {"outer": [float(v) for v in e["arm_outer_m"]],
                                   "inner": [float(v) for v in e["arm_inner_m"]]}}
            for role in ("coupler_in", "coupler_out"):
                c = couplers[(k, role)]
                item[role] = {"gap_m": c["gap_m"], "length_m": c["length_m"], "x_m": c["x_m"]}
            for kind in ("theta", "phi"):
                h = heaters[(k, kind)]
                item["heater_" + kind] = {"phi": float(h["phi"]), "length_m": h["length_m"], "x_m": h["x_m"]}
            mzis.append(item)
        layer["mzis"] = mzis
        layer["output_heaters"] = [{"mode": o["mode"], "phi": float(o["phi"]), "length_m": o["length_m"],
                                    "x_m": o["x_m"]}
                                   for o in sorted((o for o in objects_by_role("heater_out")
                                                    if o["layer_index"] == li), key=lambda o: o["mode"])]
        layers.append(layer)
    geometry["layers"] = layers
    oe = objects_by_role("oe")[0]
    geometry["optoelectronic_stage"] = {"type": oe["type"], "v_pi": oe["v_pi"], "bias": oe["bias"],
                                        "note": oe["note"]}
    ro = objects_by_role("readout")[0]
    geometry["readout"] = {"gain": float(ro["gain"]), "ports": [int(p) for p in ro["ports"]], "note": ro["note"]}
    geometry["exported_from"] = "Blender %s object custom properties" % bpy.app.version_string
    geometry["sha256"] = nc.geometry_hash(geometry)
    return geometry


def write_params(params, heaters) -> None:
    for obj, value in zip(heaters, params):
        obj["phi"] = float(value)


def keyframe_params(heaters, frame: int) -> None:
    """Keyframe a copy of phi in `phi_anim` (float32 animation channel).

    `phi` itself is never animated: an animated property is overwritten by its
    float32 F-curve whenever the file is loaded or the frame changes, which
    would corrupt the double-precision state that defines the model.
    """
    for obj in heaters:
        obj["phi_anim"] = float(obj["phi"])
        obj.keyframe_insert(data_path='["phi_anim"]', frame=frame)


def save_blend(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
