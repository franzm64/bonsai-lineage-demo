import numpy as np

def bonsai_gene_diagnostic(data, zscore_cutoff=1.0):
    """
    Mimic Bonsai's gene filtering step.
    data: shape (cells, genes)
    """

    gene_means = np.mean(data, axis=0)
    gene_stds = np.std(data, axis=0)

    # z-score of gene variability
    zscores = (gene_stds - np.mean(gene_stds)) / np.std(gene_stds)

    surviving = np.sum(zscores > zscore_cutoff)

    print("Number of genes:", data.shape[1])
    print("Genes passing z-score cutoff:", surviving)

    return surviving


def branching_tree(n_points=50, dim=5, noise=0.05, seed=None):
    """
    Generate a simple branching trajectory dataset.

    Parameters
    ----------
    n_points : int
        Total number of points.
    dim : int
        Dimension of the embedding space.
    noise : float
        Standard deviation of Gaussian noise added to extra dimensions.
    seed : int or None
        Random seed for reproducibility.
    """
    rng = np.random.default_rng(seed)

    n_branch = n_points // 2

    t = np.linspace(0, 1, n_branch)

    branch1 = np.stack([t, t * 0], axis=1)
    branch2 = np.stack([t, -t], axis=1)

    data = np.vstack([branch1, branch2])

    # embed in higher dimensions
    extra = rng.normal(0, noise, size=(n_points, dim - 2))
    data = np.hstack([data, extra])

    return data

def branching_tree_curved(n_points=50, dim=5, noise=0.05, seed=None):

    rng = np.random.default_rng(seed)

    n_branch = n_points // 2

    t = np.linspace(0, 1, n_branch)

    # curved branches
    branch1 = np.stack([
        t,
        0.5 * t**2
    ], axis=1)

    branch2 = np.stack([
        t,
        -0.5 * t**2
    ], axis=1)

    data = np.vstack([branch1, branch2])

    # small noise in the main plane
    data += rng.normal(0, noise, size=data.shape)

    # embed into higher dimensions
    if dim > 2:
        extra = rng.normal(0, noise, size=(n_points, dim - 2))
        data = np.hstack([data, extra])

    return data

import numpy as np

def branching_tree_structured(n_points=50, dim=5, noise=0.02, seed=None):
    """
    Generate a branching trajectory that encourages Bonsai
    to reconstruct long branches.
    """

    rng = np.random.default_rng(seed)

    n_branch = n_points // 2

    # more density near root
    t = np.sort(rng.beta(2, 5, n_branch))

    # base branches
    branch1 = np.stack([t, 0.6 * t**2], axis=1)
    branch2 = np.stack([t, -0.6 * t**2], axis=1)

    data = np.vstack([branch1, branch2])

    # noise increases along trajectory
    branch_noise = noise * (1 + 3 * np.repeat(t, 2))

    data += rng.normal(0, branch_noise[:, None], size=data.shape)

    # embed into higher dimensions
    if dim > 2:               # 0.3 in increased noise
        extra = rng.normal(0, 0.3, size=(n_points, dim - 2))
        data = np.hstack([data, extra])

    return data


def gaussian_clusters(n_points=500, dim=50):
    centers = np.array([
        np.zeros(dim),
        np.ones(dim)*3,
        np.ones(dim)*-3
    ])

    points = []

    for c in centers:
        pts = c + np.random.normal(0, 1, size=(n_points//3, dim))
        points.append(pts)

    return np.vstack(points)


def circular_manifold(n_points=500, dim=50):
    theta = np.linspace(0, 2*np.pi, n_points)

    x = np.cos(theta)
    y = np.sin(theta)

    base = np.stack([x, y], axis=1)

    extra = np.random.normal(0, 0.1, size=(n_points, dim-2))

    return np.hstack([base, extra])
