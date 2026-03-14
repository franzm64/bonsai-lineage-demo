import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import umap


def compute_embeddings(data):

    pca = PCA(n_components=2).fit_transform(data)

    reducer = umap.UMAP()
    um = reducer.fit_transform(data)

    return pca, um


def plot_embeddings(data, title, seed):

    pca = PCA(n_components=2).fit_transform(data)

    reducer = umap.UMAP(random_state=seed)
    um = reducer.fit_transform(data)

    fig, ax = plt.subplots(1,2, figsize=(10,4))

    ax[0].scatter(pca[:,0], pca[:,1], s=5)
    ax[0].set_title("PCA")
    ax[0].scatter(pca[:, 0], pca[:, 1], s=3)

    ax[1].scatter(um[:,0], um[:,1], s=5)
    ax[1].set_title("UMAP")
    ax[1].scatter(um[:, 0], um[:, 1], s=3)

    fig.suptitle(title)

    plt.show()

# to calculate node placement on the PCA and UMAP plots
def embedding_positions(tree, coords):

    pos = {}

    # leaf nodes
    for leaf in tree.iter_leaves():
        idx = int(leaf.name.split("_")[1])
        pos[leaf.name] = coords[idx]

    # internal nodes
    for node in tree.traverse("postorder"):

        if node.name in pos:
            continue

        children = [c for c in node.children if c.name in pos]

        if len(children) > 0:

            pts = np.array([pos[c.name] for c in children])
            pos[node.name] = pts.mean(axis=0)

    return pos

def draw_projected_tree(ax, tree, pos, color_map, max_length=1.0):

    for node in tree.traverse():

        if node.is_root():
            continue

        parent = node.up

        x1,y1 = pos[parent.name]
        x2,y2 = pos[node.name]

        # skip edges that project too long in embedding
        length = np.sqrt((x1-x2)**2 + (y1-y2)**2)

        if length > max_length:
            continue

        # choose color from subtree
        leaves = node.get_leaf_names()
        idx = int(leaves[0].split("_")[1])

        color = color_map[idx]

        ax.plot(
            [x1,x2],
            [y1,y2],
            color=color,
            linewidth=2.5,
            alpha=0.8,
            zorder=1
        )

# How many **major** branches emanate from root? (Denser data around the root may give rise to very short branches -- disregards them)
def extract_root_lineages(tree, min_size=5):

    root = tree.get_tree_root()

    lineages = []

    for child in root.children:

        leaves = [leaf.name for leaf in child.iter_leaves()]

        if len(leaves) >= min_size:
            lineages.append(leaves)

    return lineages


# determine subtree lineage
def subtree_color(node, branch_id, colors):

    leaves = node.get_leaf_names()

    ids = []

    for leaf in leaves:
        idx = int(leaf.split("_")[1])
        ids.append(branch_id[idx])

    return colors[max(set(ids), key=ids.count)]


def hierarchical_layout_centered(tree, backbone_graph):

    root = tree.get_tree_root()
    pos = {}
    x_counter = 0

    def assign(node, depth=0):

        nonlocal x_counter

        children = [
            c for c in node.children
            if c.name in backbone_graph.nodes
        ]

        if len(children) == 0:
            x = x_counter
            x_counter += 1

        else:
            xs = [assign(child, depth+1) for child in children]
            x = np.mean(xs)

        pos[node.name] = (x, -depth)

        return x

    assign(root)
    return pos


def draw_tree_on_embedding(ax, coords, tree, color_map):

    for node in tree.traverse():

        # only internal branching points
        if node.is_leaf():
            continue

        children = [c for c in node.get_children() if c.is_leaf()]

        if len(children) >= 2:

            for i in range(len(children)):
                for j in range(i+1, len(children)):

                    a = int(children[i].name.split("_")[1])
                    b = int(children[j].name.split("_")[1])

                    color = color_map[a]

                    ax.plot(
                        [coords[a,0], coords[b,0]],
                        [coords[a,1], coords[b,1]],
                        color=color,
                        linewidth=2,
                        alpha=0.8,
                        zorder=1
                    )
