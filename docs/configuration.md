# Configuration

All settings live in a single `config.yaml` at the repository root. Every key
can be overridden via the corresponding CLI flag (`--num-sampled-grasps`,
`--num-workers`, etc.).

## Pipeline parameters

| Key | Default | Description |
|---|---|---|
| `meshes_path` | `output/meshes` | Directory containing input `.obj` files (overridden by `--mesh` / `--meshes-dir`). |
| `output_path` | `output` | Output directory root. Grasp `.h5` files go under `<output_path>/grasps/`. |
| `num_sampled_grasps` | `500` | Number of candidate grasps to sample per mesh before FC filtering. |
| `num_positive` | `2000` | Maximum number of FC-passing grasps to keep. |
| `num_negative` | `2000` | Maximum number of FC-failing grasps to keep. |
| `friction_coeff` | `0.4` | Coulomb friction coefficient used in the FC optimisation's friction-cone constraint. |
| `object_mass` | `6` | Object mass in kg; gravity wrench = `10 × mass` N. |
| `num_workers` | `8` | Number of CPU worker processes for parallel FC optimisation. |
| `debug` | `false` | Enable verbose diagnostics in the antipodal grasp sampler. |

## Advanced: DexNet antipodal sampling parameters

These keys are passed directly to the `MeshAntipodalGraspSampler` in
`dexnet/grasping/grasp_sampler.py`. You generally should not need to change
them.

| Key | Default | Description |
|---|---|---|
| `sampling_friction_coef` | `0.4` | Friction coefficient used during antipodal sampling (contact cone). |
| `sampling_friction_coef_inc` | `0.1` | Increment for the friction cone when sampling. |
| `num_cone_faces` | `8` | Number of faces in the pyramidal friction-cone approximation. |
| `grasp_samples_per_surface_point` | `2` | Grasp candidates per surface point. |
| `min_contact_dist` | `0.0` | Minimum distance between the two contacts of a single jaw. |
| `coll_check_num_grasp_rots` | `20` | Rotational steps for collision checking. |
| `check_collisions` | `1` | Enable / disable collision checking during sampling. |
| `max_num_surface_points` | `6000` | Maximum number of surface points to sample. |
| `grasp_dist_thresh` | `0.0025` | Distance threshold for the antipodal criterion. |
| `grasp_dist_alpha` | `0.005` | Weight for the distance term in the antipodal score. |
| `approach_dist` | `0.05` | Gripper approach distance for collision checking. |
| `delta_approach` | `0.005` | Step size for the approach trajectory. |
