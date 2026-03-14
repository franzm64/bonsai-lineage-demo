import numpy as np
import subprocess
import yaml
import os
import networkx as nx
from pathlib import Path
import time


def run_bonsai(X, project_root):

    project_root = Path(project_root)

    input_dir = project_root / "bonsai_inputs"
    result_dir = project_root / "bonsai_results"
    tmp_dir = project_root / "bonsai_tmp"
    tmp_dir.mkdir(exist_ok=True)

    data_dir = input_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # ---------- write Bonsai input files ----------

    # np.savetxt(data_dir / "delta.txt", X.T)
    # np.savetxt(data_dir / "d_delta.txt", np.ones_like(X.T) * 0.1)
    np.savetxt(data_dir / "delta.txt", X.T, delimiter="\t", fmt="%.6f")
    np.savetxt(data_dir / "d_delta.txt", np.ones_like(X.T) * 0.1, delimiter="\t", fmt="%.6f")

    # ---------- write config ----------

    config = {
        "dataset": "synthetic_demo",
        "data_folder": str(data_dir),
        "results_folder": str(result_dir),
        "filenames_data": "delta.txt,d_delta.txt",
        "input_is_sanity_output": False,
        "use_knn": -1,
        "skip_nnn_reordering": True,
        "skip_redo_starry": True,
        "skip_opt_times": True,
        #"tmp_folder": "/home/franz/Documents/New_job/IMBA_deGroot/bonsai-geometry-study/bonsai_tmp",
        "tmp_folder": str(tmp_dir),
        "pickup_intermediate": False
    }

    config_path = input_dir / "bonsai_config.yaml"

    with open(config_path, "w") as f:
        yaml.dump(config, f)

    # ---------- run Bonsai ----------
    result = subprocess.run(
        [
            "python",
            "Bonsai-data-representation/bonsai/bonsai_main.py",
            "--config_filepath",
            str(config_path)
        ],
        cwd=project_root,
        # capture_output=True,
        text=True,
    )

    # print("STDOUT:\n", result.stdout)
    # print("STDERR:\n", result.stderr)

    result.check_returncode()

    # ---------- find resulting tree ----------

    tree_files = list(result_dir.rglob("*.nwk"))

    if not tree_files:
        raise RuntimeError("No Bonsai tree produced")

    tree_path = tree_files[-1]

    # ---------- convert tree → graph ----------

    import ete3

    # tree = ete3.Tree(str(tree_path))
    tree = ete3.Tree(str(tree_path), format=1)

    G = nx.Graph()

    for node in tree.traverse():
        for child in node.children:
            G.add_edge(node.name, child.name, weight=child.dist)

    nodes = list(G.nodes)

    dist_matrix = np.zeros((len(nodes), len(nodes)))

    for i, n1 in enumerate(nodes):
        lengths = nx.single_source_dijkstra_path_length(G, n1)
        for j, n2 in enumerate(nodes):
            dist_matrix[i, j] = lengths.get(n2, 0)

    return dist_matrix

# test
from src.synthetic_data import branching_tree_structured, branching_tree_curved, gaussian_clusters, circular_manifold
from src.visualize import plot_embeddings

# Branching structure
# this produces the shallow Bonsai figure (mapped on pca)
# seed = 30
# noise = 0.14
# data = branching_tree_curved(n_points=40, dim=4, noise=noise, seed=seed)

seed = 43
noise = 0.02
data = branching_tree_structured(n_points=50, dim=40, noise=noise, seed=seed)

plot_embeddings(data, f"Branching dataset with seed: {seed} noise: {noise}",seed)

print(type(data),data.shape)
# tic = time.perf_counter()
# D_bonsai = run_bonsai(data, "..")
# toc = time.perf_counter()
# print(f"Elapsed time: {toc - tic:.1f} [s]")
