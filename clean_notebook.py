import json

notebook_path = "visualize_grasps.ipynb"
with open(notebook_path, "r") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        cell["outputs"] = []
        cell["execution_count"] = None

with open(notebook_path, "w") as f:
    json.dump(nb, f, indent=1)

print("Notebook outputs cleared successfully.")
