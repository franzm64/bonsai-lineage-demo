import numpy as np
import sklearn
from sklearn.metrics import pairwise_distances
from scipy.stats import pearsonr

def per_point_distance_preservation(original_data, embedded_data):

    d_original = sklearn.metrics.pairwise_distances(original_data)
    d_embedded = sklearn.metrics.pairwise_distances(embedded_data)

    corrs = []

    for i in range(d_original.shape[0]):

        corr, _ = pearsonr(d_original[i], d_embedded[i])
        corrs.append(corr)

    return np.array(corrs)

def distance_preservation(original_data, embedded_data):
    """
    Compute correlation between original distances
    and distances in the embedding.
    """

    d_original = pairwise_distances(original_data)
    d_embedded = pairwise_distances(embedded_data)

    # flatten matrices
    d_original = d_original.flatten()
    d_embedded = d_embedded.flatten()

    corr, _ = pearsonr(d_original, d_embedded)

    return corr
