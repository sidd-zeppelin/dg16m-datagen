# Output format

Each input mesh `foo.obj` produces a single HDF5 file
`<output_path>/grasps/foo.h5`.

## File structure

```
/
├── grasps/
│   ├── grasps              (N, 2, 4, 4)  float64 — gripper poses
│   ├── contact_points      (N, 4, 3)     float64 — contact locations
│   ├── contact_forces      (N, 4, 3)     float64 — optimal forces
│   ├── loss_values         (N,)          float64 — FC residuals
│   ├── fc_passing_indices  (P,)          int64   — indices of passing grasps
│   └── fc_failed_indices   (F,)          int64   — indices of failing grasps
└── object/
    ├── file                scalar        str     — source mesh filename
    └── scale               scalar        float64 — scale applied to the mesh
```

- **N** = total grasps saved = `num_positive + num_negative` (or fewer if
  insufficient grasps exist).
- **P** = number of passing grasps (≤ `num_positive`).
- **F** = number of failing grasps (≤ `num_negative`).

## Dataset descriptions

### `grasps/grasps`

Gripper poses as 4×4 homogeneous transformation matrices. The first
dimension indexes grasps, the second indexes the two arms
(`0` = left, `1` = right).

Reading back with NumPy:

```python
grasps.shape   # (N, 2, 4, 4)
left_pose  = grasps[i, 0]  # 4×4 transform: gripper frame → world
right_pose = grasps[i, 1]
```

### `grasps/contact_points`

Four contact points per grasp in world coordinates. Order matches the
grasp map: the first two contacts belong to the first gripper jaw, the
last two to the second jaw.

### `grasps/contact_forces`

Optimal contact force vectors (world frame) returned by the FC solver.
Each force corresponds to the contact point at the same index.

### `grasps/loss_values`

The optimal value of the FC optimisation objective
$\|Gf + w_\text{ext}\|$. Values below `1e-5` indicate a passing grasp.
A value of exactly `1000` indicates the solver hit a degenerate case
(rank-deficient grasp map or solver failure).

### `grasps/fc_passing_indices` / `fc_failed_indices`

Indices into the first axis of the other datasets. Passing grasps are
stored first, then failing grasps:

```python
# All passing grasps
passing_grasps = grasps[fc_passing_indices]
# All failing grasps
failing_grasps = grasps[fc_failed_indices]
```

### `object/scale`

The scale factor that was applied to the raw mesh before processing.
If you load the mesh separately, apply the same scale to match the
coordinate frame used for the grasps.
