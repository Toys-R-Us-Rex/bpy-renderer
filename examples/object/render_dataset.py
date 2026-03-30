import os
import json
from pathlib import Path
from PIL import Image

from bpyrenderer.camera import add_camera
from bpyrenderer.engine import init_render_engine
from bpyrenderer.environment import set_env_map
from bpyrenderer.importer import load_file
from bpyrenderer.render_output import (
    enable_color_output,
    enable_depth_output,
    enable_normals_output,
)
from bpyrenderer import SceneManager
from bpyrenderer.camera.layout import get_camera_positions_on_sphere


# ========= PATHS =========
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = (BASE_DIR / "../..").resolve()

GLB_DIR = (ROOT_DIR / "assets/models").resolve()
ORTHO_ROOT = (ROOT_DIR / "data/Ortho10View").resolve()
OUTPUT_ROOT = (ORTHO_ROOT / "data").resolve()
ENV_PATH = (ROOT_DIR / "assets/env_textures/brown_photostudio_02_1k.exr").resolve()


# ========= INIT =========
init_render_engine("BLENDER_EEVEE")


def render_model(glb_path):
    name = glb_path.stem
    prefix = name[:2].lower()

    output_dir = OUTPUT_ROOT / prefix / name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Rendering {name} -> {output_dir} ===")

    # Reset scene
    scene_manager = SceneManager()
    scene_manager.clear(reset_keyframes=True)

    # Load model
    load_file(str(glb_path))

    # Normalize + cleanup
    scene_manager.smooth()
    scene_manager.clear_normal_map()
    scene_manager.set_material_transparency(False)
    scene_manager.set_materials_opaque()
    scene_manager.normalize_scene(1.0)

    # Environment
    set_env_map(str(ENV_PATH))

    # Cameras (6 orthographic views)
    cam_pos, cam_mats, elevations, azimuths = get_camera_positions_on_sphere(
        center=(0, 0, 0),
        radius=1.5,
        elevations=[0],
        azimuths=[item - 90 for item in [0, 45, 90, 180, 270, 315]],
    )

    cameras = []
    for i, camera_mat in enumerate(cam_mats):
        camera = add_camera(camera_mat, "ORTHO", add_frame=i < len(cam_mats) - 1)
        cameras.append(camera)

    # Outputs
    width, height = 1024, 1024

    enable_color_output(
        width,
        height,
        str(output_dir),
        file_format="WEBP",
        mode="IMAGE",
        film_transparent=True,
    )
    enable_depth_output(str(output_dir))
    enable_normals_output(str(output_dir))

    # Render
    scene_manager.render()

    # Convert normal_*.png -> normal_*.webp
    for file in os.listdir(output_dir):
        if file.startswith("normal_") and file.endswith(".png"):
            png_path = os.path.join(output_dir, file)
            webp_path = os.path.join(output_dir, file.replace(".png", ".webp"))

            with Image.open(png_path) as img:
                img.save(webp_path, "WEBP")

            if os.path.exists(png_path):
                os.remove(png_path)

    # Rename render_*.webp -> color_*.webp
    for file in os.listdir(output_dir):
        if file.startswith("render_") and file.endswith(".webp"):
            old_path = os.path.join(output_dir, file)
            new_path = os.path.join(output_dir, file.replace("render_", "color_", 1))
            os.rename(old_path, new_path)

    # Metadata
    meta_info = {"width": width, "height": height, "locations": []}

    for i in range(len(cam_pos)):
        index = f"{i:04d}"
        meta_info["locations"].append(
            {
                "index": index,
                "projection_type": cameras[i].data.type,
                "ortho_scale": cameras[i].data.ortho_scale,
                "camera_angle_x": cameras[i].data.angle_x,
                "elevation": elevations[i],
                "azimuth": azimuths[i],
                "transform_matrix": cam_mats[i].tolist(),
            }
        )

    with open(output_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=4)


def write_dataset_jsons(model_names):
    ORTHO_ROOT.mkdir(parents=True, exist_ok=True)

    list_6w_path = ORTHO_ROOT / "list_6w.json"
    captions_path = ORTHO_ROOT / "captions.json"

    model_names = sorted(model_names)

    with open(list_6w_path, "w", encoding="utf-8") as f:
        json.dump(model_names, f, indent=2, ensure_ascii=False)

    captions_data = {name: "" for name in model_names}
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(captions_data, f, indent=2, ensure_ascii=False)

    print(f"\nWrote: {list_6w_path}")
    print(f"Wrote: {captions_path}")


# ========= MAIN LOOP =========
if __name__ == "__main__":
    glb_files = sorted(GLB_DIR.glob("*.glb"))
    model_names = [glb.stem for glb in glb_files]

    print(f"Found {len(glb_files)} models")

    for glb in glb_files:
        try:
            render_model(glb)
        except Exception as e:
            print(f"Failed on {glb.name}: {e}")

    write_dataset_jsons(model_names)