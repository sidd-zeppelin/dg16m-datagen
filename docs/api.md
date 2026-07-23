# API reference

## 1. `generate_dg16m.f()`

Orchestrates the full pipeline: load mesh, sample antipodal grasps, run
FC optimisation, filter, and save `.h5`.

```python
f(OBJ_FILENAME, SAVE_PATH, return_grasps=False, num_sampled_grasps=500,
  num_workers=8, gripper_name="robotiq_85", num_positive=2000,
  num_negative=2000, friction_coeff=0.4, object_mass=6,
  dexnet_config=None) -> tuple[int, int]
```

| Argument | Type | Default | Description |
|---|---|---|---|
| `OBJ_FILENAME` | `str` | — | Path to input `.obj` mesh |
| `SAVE_PATH` | `str` | — | Output directory for `.h5` files |
| `return_grasps` | `bool` | `False` | Return raw grasps instead of running FC |
| `num_sampled_grasps` | `int` | `500` | Candidate grasps to sample per mesh |
| `num_workers` | `int` | `8` | Workers for parallel FC |
| `gripper_name` | `str` | `"robotiq_85"` | Gripper model |
| `num_positive` | `int` | `2000` | Max FC-passing grasps to save |
| `num_negative` | `int` | `2000` | Max FC-failing grasps to save |
| `friction_coeff` | `float` | `0.4` | Coulomb friction coefficient |
| `object_mass` | `float` | `6` | Object mass in kg |
| `dexnet_config` | `dict \| None` | `None` | Extra config for antipodal sampler |

**Returns** `(num_passing, num_failing)` — number of grasps saved in each category.

---

## 2. `grasp_optimization.check_contact_points_parallel.run_fc_optimization()`

Project contact points onto the mesh surface to get normals, then solve
the FC convex optimisation in parallel.

```python
run_fc_optimization(mesh, contact_points, object_mass=6,
                    friction_coeff=0.4, orientation=0,
                    num_workers=8) -> tuple
```

| Argument | Type | Default | Description |
|---|---|---|---|
| `mesh` | `trimesh.Trimesh` | — | Scaled, centred object mesh |
| `contact_points` | `np.ndarray` | — | `(N, 4, 3)` — four contact points per grasp |
| `object_mass` | `float` | `6` | Mass in kg (gravity wrench = `10 × mass` N) |
| `friction_coeff` | `float` | `0.4` | Coulomb friction coefficient |
| `orientation` | `int` | `0` | Gravity direction: `0` → `-z`, `1` → `-y`, `2` → `-x` |
| `num_workers` | `int` | `8` | Worker processes |

**Returns** `(passing_indices, loss_values, contact_forces, frames)`

| Return | Shape | Description |
|---|---|---|
| `passing_indices` | `list[int]` | Indices of grasps with loss < 1e-5 |
| `loss_values` | `(N,)` | Residual wrench norm per grasp |
| `contact_forces` | `(N, 4, 3)` | Optimal contact force vectors (world) |
| `frames` | `(N, 4, 4, 4)` | 4×4 contact-frame transforms per grasp |

---

## 3. `grasp_optimization.force_closure_optmization`

### 3.1 `fc_optimization()`

Solve the FC convex optimisation for a single 4-contact grasp. Minimises
`‖ Gf + w_ext ‖` subject to friction-cone SOC constraints and force limits
(`≤ 70 N`). Returns `loss=1000` if the grasp map is rank-deficient or
the solver fails.

```python
fc_optimization(contact_positions, contact_normals, weight,
                friction_coeff=0.3, soft_contact=False,
                orientation=0) -> tuple
```

| Argument | Type | Default | Description |
|---|---|---|---|
| `contact_positions` | `np.ndarray` | — | `(4, 3)` — contact points |
| `contact_normals` | `np.ndarray` | — | `(4, 3)` — inward surface normals |
| `weight` | `float` | — | Gravity wrench magnitude (typically `10 × mass`) |
| `friction_coeff` | `float` | `0.3` | Coulomb friction coefficient |
| `soft_contact` | `bool` | `False` | Use 4-D (soft) or 3-D force basis |
| `orientation` | `int` | `0` | Gravity direction |

**Returns** `(f1, f2, f3, f4, loss, contact_frames)`

| Return | Shape | Description |
|---|---|---|
| `f1`–`f4` | `(3,)` each | Optimal contact forces (world frame) |
| `loss` | `float` | Residual wrench norm (1000 on failure) |
| `contact_frames` | `list[ndarray]` | Four 4×4 contact-frame transforms |

### 3.2 `compute_grasp_map()`

Build the grasp map *G* from contact positions and inward normals using
the point-contact-with-friction model.

```python
compute_grasp_map(contact_pos, contact_normal,
                  soft_contact=False) -> tuple
```

| Argument | Type | Default | Description |
|---|---|---|---|
| `contact_pos` | `list[ndarray]` | — | Contact locations in object frame |
| `contact_normal` | `list[ndarray]` | — | Inward surface normals `(N, 3)` |
| `soft_contact` | `bool` | `False` | Soft-contact model (4-D basis) |

**Returns** `(G, contact_frames)`

| Return | Shape | Description |
|---|---|---|
| `G` | `(6, N × d)` | Grasp map (*d* = 3 for hard, 4 for soft contact) |
| `contact_frames` | `list[ndarray]` | 4×4 transforms for each contact |

### 3.3 `generate_contact_frame()`

Build a 4×4 homogeneous frame with z-axis aligned to the surface normal
(inward-pointing).

```python
generate_contact_frame(pos, normal) -> np.ndarray
```

| Argument | Type | Description |
|---|---|---|
| `pos` | `np.ndarray` | Contact position `(3,)` |
| `normal` | `np.ndarray` | Surface normal direction `(3,)` |

**Returns** `(4, 4)` — contact frame transform.

### 3.4 `adj_T()`

Compute the 6×6 adjoint matrix of a 4×4 homogeneous transform. Used to
map contact forces from the contact frame to the object frame in the
grasp map construction.

```python
adj_T(frame) -> np.ndarray
```

| Argument | Type | Description |
|---|---|---|
| `frame` | `np.ndarray` | 4×4 homogeneous transform |

**Returns** `(6, 6)` — adjoint matrix.

### 3.5 `normalize()`

Unit-normalise a 3-D vector.

```python
normalize(x) -> np.ndarray
```

| Argument | Type | Description |
|---|---|---|
| `x` | `np.ndarray` | Input vector `(3,)` |

**Returns** `(3,)` — unit vector (zero-magnitude returns `x / 1e-10`).

### 3.6 `hat()`

Skew-symmetric (hat) matrix such that `[v]ₓ w = v × w`.

```python
hat(v) -> np.ndarray
```

| Argument | Type | Description |
|---|---|---|
| `v` | `np.ndarray` | 3-D vector `(3,)` or `(3, 1)` |

**Returns** `(3, 3)` — skew-symmetric matrix.
