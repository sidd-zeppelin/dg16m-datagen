import sys
import os
import shutil
import yaml
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "core", "scripts"))

# pyrefly: ignore [missing-import]
from generate_dg16m import f as generate_grasps_for_mesh

def main():
    parser = argparse.ArgumentParser(description="DG16M Data Generation CLI")
    parser.add_argument("--mesh", type=str, help="Path to a single .obj file")
    parser.add_argument("--meshes-dir", type=str, help="Path to a directory containing .obj files")
    parser.add_argument("--output-dir", type=str, help="Where to save the .h5 grasps and copied meshes")
    parser.add_argument("--num-workers", type=int, help="Number of CPU workers for parallelization")
    parser.add_argument("--target-grasps", type=int, help="Number of initial grasps to sample")
    
    args = parser.parse_args()

    config_path = os.path.join(script_dir, "config.yaml")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file) or {}

    target_num_grasps = args.target_grasps if args.target_grasps is not None else config.get("target_num_grasps", 500)
    num_workers = args.num_workers if args.num_workers is not None else config.get("num_workers", 8)
    gripper_name = config.get("gripper", "robotiq_85")
    
    out_dir_raw = args.output_dir if args.output_dir else config.get("output_path", "output")
    output_path = os.path.abspath(os.path.join(script_dir, out_dir_raw))
    
    meshes_dir_raw = args.meshes_dir if args.meshes_dir else config.get("meshes_path", "meshes")
    default_meshes_path = os.path.abspath(os.path.join(script_dir, meshes_dir_raw))

    output_meshes_path = os.path.join(output_path, "meshes")
    output_grasps_path = os.path.join(output_path, "grasps")
    
    os.makedirs(output_meshes_path, exist_ok=True)
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
        single_object = config.get("single_object")
        if single_object:
            if not single_object.endswith(".obj"):
                single_object += ".obj"
            if os.path.exists(os.path.join(meshes_path, single_object)):
                objects_to_process.append(single_object)
            else:
                print(f"Single object {single_object} not found in {meshes_path}")
                return
        else:
            if not os.path.exists(meshes_path):
                print(f"Input meshes directory not found: {meshes_path}")
                return
            objects_to_process = [obj for obj in os.listdir(meshes_path) if obj.endswith(".obj")]
            objects_to_process.sort()

    os.chdir(os.path.join(script_dir, "core", "scripts"))
    
    for obj in objects_to_process:
        input_mesh_file = os.path.join(meshes_path, obj)
        output_mesh_file = os.path.join(output_meshes_path, obj)
        
        shutil.copy2(input_mesh_file, output_mesh_file)
        print(f"Copied mesh to: {output_mesh_file}")
        
        print(f"Generating grasps for: {obj}")
        num_passing, num_failed = generate_grasps_for_mesh(
            OBJ_FILENAME=input_mesh_file,
            SAVE_PATH=output_grasps_path,
            return_grasps=False,
            target_num_grasps=target_num_grasps,
            num_workers=num_workers,
            gripper_name=gripper_name
        )
        print(f"Finished {obj}: passing: {num_passing}, failed: {num_failed}")

if __name__ == "__main__":
    main()