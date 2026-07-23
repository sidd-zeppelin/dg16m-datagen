"""DG16M grasp generation orchestration.

This module ties together Dex-Net antipodal grasp sampling with a
force-closure optimization step to produce the final DG16M dataset.

The main entry point is :func:`f`, which:
  1. Loads the mesh from an ``.obj`` file.
  2. Samples dual-arm antipodal grasps via the Dex-Net mesh antipodal sampler.
  3. Runs force-closure optimization on every sampled grasp.
  4. Selects *num_positive* passing and *num_negative* failing grasps.
  5. Saves the result as an ``.h5`` file.
"""

import os
import numpy as np
from dexnet.grasping import GraspableObject3D, RobotGripper
from meshpy import ObjFile
import h5py
from dexnet.api import DexNet
from grasp_optimization.check_contact_points_parallel import run_fc_optimization
import trimesh


def f(OBJ_FILENAME, SAVE_PATH, return_grasps=False, num_sampled_grasps=500, num_workers=8,
      gripper_name="robotiq_85", num_positive=2000, num_negative=2000,
      friction_coeff=0.4, object_mass=6, dexnet_config=None):
    """Generate dual-arm grasps for a single mesh and save to disk.

    The pipeline consists of:

    1. **Load** — read the mesh from ``OBJ_FILENAME`` via meshpy.
    2. **Sample** — run the Dex-Net mesh antipodal sampler to produce
       *num_sampled_grasps* candidate dual-arm grasps.
    3. **Force-closure check** — for each grasp pair, solve a convex
       optimisation (cvxpy) to find contact forces that resist gravity.
       A grasp *passes* if the residual wrench norm is below
       ``1e-5``.
    4. **Select** — keep up to *num_positive* passing grasps (random
       subsample) and up to *num_negative* failing grasps (highest-loss
       subsample).
    5. **Save** — write the selected grasps, contact points, contact
       forces, and loss values to an HDF5 file named after the mesh.

    Args:
        OBJ_FILENAME (str): Path to the input ``.obj`` mesh file.
        SAVE_PATH (str): Directory to write the ``.h5`` output file to.
        return_grasps (bool): If ``True``, return raw grasp data instead
            of running FC optimisation. Used for debugging.
        num_sampled_grasps (int): Number of candidate grasps to sample
            per object (before FC filtering).
        num_workers (int): Number of parallel workers for FC optimisation.
        gripper_name (str): Gripper model to use. Only ``"robotiq_85"``
            ships with the repo.
        num_positive (int): Maximum number of FC-passing grasps to keep.
        num_negative (int): Maximum number of FC-failing grasps to keep.
        friction_coeff (float): Coulomb friction coefficient used in the
            FC optimisation's friction-cone constraint.
        object_mass (float): Object mass in kg; used to set the gravity
            wrench magnitude (``10 * mass`` N).
        dexnet_config (dict | None): Additional configuration keys passed
            to the Dex-Net antipodal sampler (e.g. ``sampling_friction_coef``,
            ``num_cone_faces``). Falls back to an empty dict.

    Returns:
        tuple[int, int]: Number of FC-passing and FC-failing grasps saved.
    """
    config = dict(dexnet_config or {})
    config['grasp_sampler'] = 'mesh_antipodal'
    config['target_num_grasps'] = num_sampled_grasps

    gripper = RobotGripper.load(gripper_name, "./grippers")

    def mesh_antipodal_grasp_sampler():
        of = ObjFile(OBJ_FILENAME)
        mesh = of.read()

        obj = GraspableObject3D(None, mesh)
        print("  sampling grasps")
        scale, grasps = DexNet._single_obj_grasps(None, obj, gripper, config, stable_pose_id=None, target_num_grasps=num_sampled_grasps, num_workers=8)

        return scale, grasps, gripper


    scale, g, gripper = mesh_antipodal_grasp_sampler()
    
    g = np.array(g)
    contact_points = np.array([(g[i][0].grasp_point1, g[i][0].grasp_point2, 
                              g[i][1].grasp_point1, g[i][1].grasp_point2) for i in range(len(g))])
    grasp_transforms = np.array([((g[i][0].gripper_pose(gripper) * gripper.T_mesh_gripper.inverse()).matrix, 
                                  (g[i][1].gripper_pose(gripper) * gripper.T_mesh_gripper.inverse()).matrix) for i in range(len(g))])
    
    if return_grasps:
        return grasp_transforms, contact_points
    
    mesh = trimesh.load(OBJ_FILENAME)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    mesh.apply_scale(scale)
    mesh.apply_translation(-mesh.centroid)
    
    fc_passing_indices, loss_values, contact_forces, frames = run_fc_optimization(mesh=mesh, 
                                                                                  contact_points=contact_points, 
                                                                                  num_workers=num_workers,
                                                                                  friction_coeff=friction_coeff,
                                                                                  object_mass=object_mass)
    fc_failed_indices = [i for i in range(len(contact_points)) if i not in fc_passing_indices]
    
    if len(fc_passing_indices) > num_positive:
        fc_passing_indices = np.random.choice(fc_passing_indices, num_positive, replace=False)
        
    fc_passing_grasps = grasp_transforms[fc_passing_indices]
    fc_passing_contact_points = contact_points[fc_passing_indices]
    fc_passing_contact_forces = contact_forces[fc_passing_indices]
    fc_passing_losses = loss_values[fc_passing_indices]
        
    
    if len(fc_failed_indices) > num_negative:
        # fc_failed_indices = np.argsort(loss_values)[-min(10000, len(fc_failed_indices)):]]
        # fc_failed_indices = np.argsort(loss_values)[-int(len(loss_values)/2):]
        fc_failed_indices = np.where(np.array(loss_values) > 0.5)[0]
        if len(fc_failed_indices) > num_negative:
            fc_failed_indices = np.random.choice(fc_failed_indices, num_negative, replace=False)

    fc_failed_grasps = grasp_transforms[fc_failed_indices]
    fc_failed_contact_points = contact_points[fc_failed_indices]
    fc_failed_contact_forces = contact_forces[fc_failed_indices]
    fc_failed_losses = loss_values[fc_failed_indices]
    
    
    filename = os.path.join(SAVE_PATH, OBJ_FILENAME.split('.obj')[0].split('/')[-1] + '.h5')
    
    print("  saved -> {}".format(filename))
    data = h5py.File(filename, 'w')
    temp1 = data.create_group("grasps")
    temp1['grasps'] = np.concatenate((fc_passing_grasps, fc_failed_grasps), axis=0) # 4000, 2, 4, 4
    temp1['contact_points'] = np.concatenate((fc_passing_contact_points, fc_failed_contact_points), axis=0) # 4000, 4, 3
    temp1['contact_forces'] = np.concatenate((fc_passing_contact_forces, fc_failed_contact_forces), axis=0) # 4000, 4, 3
    temp1['loss_values'] = np.concatenate((fc_passing_losses, fc_failed_losses), axis=0) # 4000
    temp1['fc_passing_indices'] = np.array([i for i in range(len(fc_passing_indices))]) # 0-1999: passing
    temp1['fc_failed_indices'] = np.array([i for i in range(len(fc_passing_indices), 
                                                            len(fc_passing_indices) + len(fc_failed_indices))]) # 2000-3999: failed 
    
    temp2 = data.create_group("object")
    temp2["file"] = OBJ_FILENAME.split('/')[-1]
    temp2["scale"] = scale
    
    return len(fc_passing_indices), len(fc_failed_indices)
