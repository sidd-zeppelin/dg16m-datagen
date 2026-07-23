import numpy as np
from tqdm import tqdm
from grasp_optimization.force_closure_optmization import fc_optimization
import concurrent.futures

LOSS_THRESHOLD = 1e-5


def run_fc_optimization(mesh, contact_points, object_mass=6, friction_coeff=0.4, orientation=0, num_workers=8):
    """Run force-closure optimisation on a set of candidate grasps in parallel.

    For each grasp (4 contact points) the function:
      1. Projects the contact points onto the mesh surface to obtain
         face normals (the friction-cone axis).
      2. Spawns a :class:`concurrent.futures.ProcessPoolExecutor` to
         solve the convex FC problem (via :func:`fc_optimization`) for
         every grasp in parallel.
      3. Classifies a grasp as *passing* if the optimal residual wrench
         norm is below ``1e-5``.

    Args:
        mesh (trimesh.Trimesh): The object mesh, scaled and centred.
        contact_points (np.ndarray): Array of shape ``(N, 4, 3)`` with
            the four contact points (world frame) for each of ``N`` grasps.
        object_mass (float): Object mass in kg. The gravity wrench is
            set to ``10 * mass`` N in the negative z-direction.
        friction_coeff (float): Coulomb friction coefficient for the
            friction-cone second-order-cone constraints.
        orientation (int): Gravity direction selector.
            ``0`` → gravity along ``-z``,
            ``1`` → gravity along ``-y``,
            ``2`` → gravity along ``-x``.
        num_workers (int): Number of worker processes.

    Returns:
        tuple:
            - **force_closure_passing_indices** (:obj:`list` of :obj:`int`):
              Indices of grasps that passed FC.
            - **loss_values** (:obj:`np.ndarray`): Residual wrench norm
              for every grasp ``(N,)``.
            - **contact_forces** (:obj:`np.ndarray`): Optimal contact
              forces ``(N, 4, 3)`` (world frame).
            - **frames** (:obj:`np.ndarray`): Contact frames ``(N, 4, 4, 4)``.
    """
    force_closure_passing_indices = []
    loss_values = []
    contact_forces = []
    frames = []

    contact_normals = np.zeros((len(contact_points), 4, 3))
    face1 = mesh.nearest.on_surface(contact_points[:, 0, :])[-1]
    face2 = mesh.nearest.on_surface(contact_points[:, 1, :])[-1]
    face3 = mesh.nearest.on_surface(contact_points[:, 2, :])[-1]
    face4 = mesh.nearest.on_surface(contact_points[:, 3, :])[-1]

    contact_normals[:, 0, :] = mesh.face_normals[face1]
    contact_normals[:, 1, :] = mesh.face_normals[face2]
    contact_normals[:, 2, :] = mesh.face_normals[face3]
    contact_normals[:, 3, :] = mesh.face_normals[face4]

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(fc_optimization,
                                    contact_points,
                                    contact_normals,
                                    [10 * object_mass] * len(contact_points),
                                    [friction_coeff] * len(contact_points),
                                    [False] * len(contact_points),
                                    [orientation] * len(contact_points)))

    for i in tqdm(range(len(results))):
        f1, f2, f3, f4, loss, frame = results[i]
        if f1 is not None and f2 is not None and f3 is not None and f4 is not None:
            if loss < LOSS_THRESHOLD:
                force_closure_passing_indices.append(i)

        loss_values.append(loss)
        contact_forces.append([f1, f2, f3, f4])
        frames.append(frame)

    print("  force closure: {} / {} passed".format(len(force_closure_passing_indices), len(contact_points)))

    loss_values = np.array(loss_values)
    contact_forces = np.array(contact_forces)
    frames = np.array(frames)

    return force_closure_passing_indices, loss_values, contact_forces, frames