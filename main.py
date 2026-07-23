import sys
import os
import time
import yaml
import argparse
import logging

logging.getLogger("autolab_core").setLevel(logging.ERROR)
logging.getLogger("dexnet").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)


def _fmt_duration(seconds):
    """Format a duration in seconds into a human-readable string.

    Args:
        seconds (float): Duration in seconds.

    Returns:
        str: Formatted string like ``"3m 12s"`` or ``"1h 5m 0s"``.
    """
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s"

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "core", "scripts"))

from generate_dg16m import f as generate_grasps_for_mesh


def main():
    """Entry point for the DG16M grasp generation pipeline.

    Parses CLI arguments and config, then runs :func:`generate_dg16m.f`
    on each input mesh. Supports single-object mode (``--mesh``) and
    batch mode (``--meshes-dir``).

    Logging from third-party libraries (autolab_core, dexnet) is silenced
    at entry to reduce noise.
    """
    parser = argparse.ArgumentParser(description="DG16M Data Generation CLI")
    parser.add_argument("--mesh", type=str, help="Path to a single .obj file")
    parser.add_argument("--meshes-dir", type=str, help="Path to a directory containing .obj files")
    parser.add_argument("--output-dir", type=str, help="Where to save the .h5 grasps and copied meshes")
    parser.add_argument("--num-workers", type=int, help="Number of CPU workers for parallelization")
    parser.add_argument("--num-sampled-grasps", type=int, help="Number of grasps to sample per object")
    parser.add_argument("--num-positive", type=int, help="Number of force-closure-passing grasps to save per object")
    parser.add_argument("--num-negative", type=int, help="Number of failing grasps to save per object")
    parser.add_argument("--debug", action=argparse.BooleanOptionalAction, default=None, help="Enable verbose sampler diagnostics")
    
    args = parser.parse_args()

    config_path = os.path.join(script_dir, "config.yaml")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file) or {}

    num_sampled_grasps = args.num_sampled_grasps if args.num_sampled_grasps is not None else config.get("num_sampled_grasps", 500)
    num_positive = args.num_positive if args.num_positive is not None else config.get("num_positive", 2000)
    num_negative = args.num_negative if args.num_negative is not None else config.get("num_negative", 2000)
    friction_coeff = config.get("friction_coeff", 0.4)
    object_mass = config.get("object_mass", 6)
    num_workers = args.num_workers if args.num_workers is not None else config.get("num_workers", 8)
    debug = args.debug if args.debug is not None else config.get("debug", False)

    os.environ["DG16M_DEBUG"] = "1" if debug else ""
    import dexnet.grasping.grasp_sampler as _grasp_sampler
    _grasp_sampler._DEBUG = bool(debug)
    
    out_dir_raw = args.output_dir if args.output_dir else config.get("output_path", "output")
    output_path = os.path.abspath(os.path.join(script_dir, out_dir_raw))
    
    meshes_dir_raw = args.meshes_dir if args.meshes_dir else config.get("meshes_path", "meshes")
    default_meshes_path = os.path.abspath(os.path.join(script_dir, meshes_dir_raw))

    output_grasps_path = os.path.join(output_path, "grasps")
    os.makedirs(output_grasps_path, exist_ok=True)

    objects_to_process = []
    meshes_path = default_meshes_path

    if args.mesh:
        mesh_path = os.path.abspath(args.mesh)
        if not os.path.exists(mesh_path):
            print(f"Mesh not found: {mesh_path}")
            return
        meshes_path = os.path.dirname(mesh_path)
        objects_to_process.append(os.path.basename(mesh_path))
    else:
        if not os.path.exists(meshes_path):
            print(f"Input meshes directory not found: {meshes_path}")
            return
        objects_to_process = [obj for obj in os.listdir(meshes_path) if obj.endswith(".obj")]
        objects_to_process.sort()

    os.chdir(os.path.join(script_dir, "core", "scripts"))

    if not objects_to_process:
        return

    print("DG16M grasp generation")
    if args.mesh:
        print(f"  mesh:     {os.path.basename(args.mesh)}")
    elif len(objects_to_process) == 1:
        print(f"  mesh:     {objects_to_process[0]}")
    else:
        print(f"  meshes:   {meshes_path} ({len(objects_to_process)} files)")
    print(f"  output:   {output_grasps_path}")
    print(f"  config:   sampled={num_sampled_grasps}  pos={num_positive} neg={num_negative}  workers={num_workers}")
    print()

    total_start = time.time()

    for i, obj in enumerate(objects_to_process, 1):
        input_mesh_file = os.path.join(meshes_path, obj)
        prefix = f"[{i}/{len(objects_to_process)}] " if len(objects_to_process) > 1 else ""
        print(f"{prefix}{obj}")
        obj_start = time.time()
        num_passing, num_failed = generate_grasps_for_mesh(
            OBJ_FILENAME=input_mesh_file,
            SAVE_PATH=output_grasps_path,
            return_grasps=False,
            num_sampled_grasps=num_sampled_grasps,
            num_workers=num_workers,
            num_positive=num_positive,
            num_negative=num_negative,
            friction_coeff=friction_coeff,
            object_mass=object_mass,
            dexnet_config=config,
        )
        print(f"  result: {num_passing} passing, {num_failed} failed")
        print(f"  took {_fmt_duration(time.time() - obj_start)}")
        print()

    total_elapsed = time.time() - total_start
    n = len(objects_to_process)
    print(f"Done: {n} object{'s' if n != 1 else ''} in {_fmt_duration(total_elapsed)}")

if __name__ == "__main__":
    main()