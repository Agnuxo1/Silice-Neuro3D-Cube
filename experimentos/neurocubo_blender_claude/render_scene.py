"""Presentation render of a trained neuro-cube (EEVEE; run only through the GPU queue).

blender -b trained_res47_N8.blend --python render_scene.py -- --model M.json --benchmark B.json
        --data-dir DATA --task res47 --n 8 --still OUT.png [--video OUT.mp4 --trajectory T.npz]

Light in each guide segment is an emission whose strength is proportional to
the optical power that the NUMERICAL MODEL computes for one real test example
(layer 1: amplitude-encoded input; layer 2: MZM re-emitted field). The render
engine does not compute any physics here; it only draws model numbers.
Lateral positions are exaggerated x20 for visibility (see nc_blender).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nc_blender as ncb  # noqa: E402
import numpy as np  # noqa: E402
import neurocubo_core as nc  # noqa: E402

bpy = ncb.bpy
GUIDE_RGB = (0.20, 0.65, 1.0)
LAYER2_RGB = (1.0, 0.55, 0.15)


def material(name, rgb, emission=0.0, alpha=1.0, metallic=0.0, roughness=0.4, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    for key in ("Emission Color", "Emission"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = (*rgb, 1.0)
            break
    bsdf.inputs["Emission Strength"].default_value = emission
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["IOR"].default_value = nc.N0
    if alpha < 1.0:
        for attr, value in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
            if hasattr(mat, attr):
                try:
                    setattr(mat, attr, value)
                except TypeError:
                    pass
    return mat, bsdf


def guide_powers(params, cfg, x_row):
    """Power per (layer, mode, column) from the model, columns 1..stages+1 (output section)."""
    n = cfg.n
    out = {}
    p1, p2 = params[:n * n], params[n * n:]
    rows1 = nc.layer_mode_powers(p1, cfg.specs[0], np.asarray(x_row, complex))
    t1, _ = nc.mesh_transfer(p1, cfg.specs[0])
    i1 = np.abs(t1 @ np.asarray(x_row, float)) ** 2
    a = np.cos(0.5 * (math.pi * i1 / cfg.v_pi + cfg.bias))
    rows2 = nc.layer_mode_powers(p2, cfg.specs[1], a.astype(complex))
    for li, rows in enumerate((rows1, rows2)):
        for col in range(1, rows.shape[0] + 1):
            for mode in range(n):
                out[(li, mode, col)] = float(rows[min(col - 1, rows.shape[0] - 1), mode])
    return out


def setup_scene(args):
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = args.width, args.height
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("NC_World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.006, 0.010, 0.022, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    try:
        scene.use_nodes = True
        tree = scene.node_tree
        rl, comp = tree.nodes.get("Render Layers"), tree.nodes.get("Composite")
        glare = tree.nodes.new("CompositorNodeGlare")
        glare.glare_type = "BLOOM" if "BLOOM" in [i.identifier for i in glare.bl_rna.properties["glare_type"].enum_items] else "FOG_GLOW"
        glare.quality = "HIGH"
        tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
        tree.links.new(glare.outputs["Image"], comp.inputs["Image"])
    except Exception as error:  # presentation only
        print("glare skipped:", error)
    side = ncb.objects_by_role("cube")[0]["side_m"] * ncb.MM
    cam_data = bpy.data.cameras.new("NC_Camera")
    cam_data.lens = 50
    cam = bpy.data.objects.new("NC_Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (side * 0.5 - side * 0.75, -side * 1.15, side * 0.62)
    target = bpy.data.objects.new("NC_Target", None)
    scene.collection.objects.link(target)
    target.location = (side * 0.5, 0, -side * 0.18)
    track = cam.constraints.new("TRACK_TO")
    track.target = target
    scene.camera = cam
    for loc, energy in (((side * 0.2, -side, side), 2.5e5), ((side, side, side * 0.8), 1.2e5)):
        light = bpy.data.objects.new("NC_Light", bpy.data.lights.new("NC_Light", "AREA"))
        light.data.energy = energy
        light.data.size = side * 0.5
        light.location = loc
        light.constraints.new("TRACK_TO").target = target
        scene.collection.objects.link(light)
    cube = ncb.objects_by_role("cube")[0]
    cube.display_type = "TEXTURED"
    glass, _ = material("NC_Glass", (0.80, 0.90, 1.0), alpha=0.10, roughness=0.05)
    cube.data.materials.append(glass)
    gold, _ = material("NC_Heater", (0.95, 0.70, 0.25), metallic=1.0, roughness=0.25)
    for o in ncb.objects_by_role("heater") + ncb.objects_by_role("heater_out"):
        o.data.materials.append(gold)
    dark, _ = material("NC_Electronics", (0.05, 0.05, 0.06), roughness=0.5)
    for role in ("oe", "readout", "input"):
        for o in ncb.objects_by_role(role):
            o.data.materials.append(dark)
    for o in ncb.objects_by_role("coupler"):
        o.hide_render = True
    guides = {}
    for o in ncb.objects_by_role("guide"):
        rgb = GUIDE_RGB if o["layer_index"] == 0 else LAYER2_RGB
        mat, bsdf = material("NC_" + o.name, rgb, emission=1.0)
        o.data.materials.append(mat)
        guides[(o["layer_index"], o["mode"], o["column"])] = bsdf
    font = bpy.data.curves.new("NC_Text", "FONT")
    text = bpy.data.objects.new("NC_Text", font)
    font.size = side * 0.035
    text.location = (side * 0.02, -side * 0.55, side * 0.05)
    text.rotation_euler = (math.radians(70), 0, 0)
    white, _ = material("NC_TextMat", (0.9, 0.93, 1.0), emission=2.0)
    font.materials.append(white)
    scene.collection.objects.link(text)
    track_t = text.constraints.new("TRACK_TO")
    track_t.target = cam
    track_t.track_axis, track_t.up_axis = "TRACK_Z", "UP_Y"
    return scene, guides, font


def apply_powers(guides, powers, scale):
    for key, bsdf in guides.items():
        bsdf.inputs["Emission Strength"].default_value = 0.05 + scale * powers.get(key, 0.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--task", default="res47")
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--still", type=Path, required=True)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--trajectory", type=Path)
    parser.add_argument("--frames", type=int, default=96)
    parser.add_argument("--width", type=int, default=3000)
    parser.add_argument("--height", type=int, default=1688)
    args = parser.parse_args(ncb.script_args())
    model = json.loads(args.model.read_text(encoding="utf-8"))
    cfg, params = nc.config_from_geometry(model)
    report = json.loads(args.benchmark.read_text(encoding="utf-8"))
    resp = report["responses"] if report["responses"]["n"] == args.n else report["responses_other_size"]
    example = next(e for e in resp["examples"] if e["correct"])
    with np.load(args.data_dir / args.task / ("test_X_N%d.npz" % args.n)) as d:
        x_row = d["X"][example["test_position"]]
    digits = {"res47": [4, 5, 6, 7], "dev03": [0, 1, 2, 3]}.get(args.task, [0, 1, 2, 3])
    scene, guides, font = setup_scene(args)
    powers = guide_powers(params, cfg, x_row)
    scale = 6.0 / max(powers.values())
    apply_powers(guides, powers, scale)
    font.body = ("Neuro-cube N=%d (numerical model)  |  test digit %d -> predicted %d\n"
                 "glow = model-computed optical power; lateral scale x20"
                 % (args.n, digits[example["true"]], digits[example["predicted"]]))
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(args.still)
    bpy.ops.render.render(write_still=True)
    if args.video and args.trajectory:
        with np.load(args.trajectory) as d:
            phases, loss = d["phases"].astype(float), d["loss"]
        picks = np.unique(np.round(np.geomspace(1, len(phases), args.frames)).astype(int) - 1)
        heaters = ncb.heater_objects([cfg.specs[0].n_mzi] * 2)
        frames = []
        for it in picks:
            p = phases[it]
            frames.append((it, float(loss[it]), guide_powers(p, cfg, x_row), p))

        def on_frame(scn, *_):
            k = min(max(scn.frame_current - 1, 0), len(frames) - 1)
            it, lval, pw, p = frames[k]
            apply_powers(guides, pw, scale)
            for obj, value in zip(heaters, p):
                obj["phi"] = float(value)
            font.body = ("Training inside Blender  |  iteration %d  |  cross-entropy %.4f\n"
                         "N=%d neuro-cube, glow = model-computed power for one test digit %d"
                         % (it, lval, args.n, digits[example["true"]]))

        bpy.app.handlers.frame_change_pre.append(on_frame)
        scene.frame_start, scene.frame_end = 1, len(frames)
        scene.render.fps = 24
        scene.render.resolution_x, scene.render.resolution_y = 1280, 720
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.filepath = str(args.video)
        bpy.ops.render.render(animation=True)
    print("NEUROCUBO_RENDER", json.dumps({"still": str(args.still), "video": str(args.video)}))


if __name__ == "__main__":
    main()
