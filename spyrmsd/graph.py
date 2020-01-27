from typing import Any, Dict, List

import networkx as nx
import numpy as np
import qcelemental as qcel

# TODO: Move elsewhere?
connectivity_tolerance: float = 0.4


def graph_from_adjacency_matrix(adjacency_matrix: np.ndarray) -> nx.Graph:
    """
    Graph from adjacency matrix.

    Parameters
    ----------
    adjacency_matrix: np.ndarray
        Adjacency matrix

    Returns
    -------
    nx.Graph
        NetworkX graph
    """

    return nx.convert_matrix.from_numpy_array(adjacency_matrix)


def adjacency_matrix_from_atomic_coordinates(
    atomicnums: np.ndarray, coordinates: np.ndarray
) -> np.ndarray:
    """
    Compute adjacency matrix from atomic coordinates.

    Parameters
    ----------
    atomicnums: numpy.ndarray
        Atomic numbers
    coordinates: numpy.ndarray
        Atomic coordinates

    Returns
    -------
    numpy.ndarray
        Adjacency matrix

    Notes
    -----
    This function is based on a very simple bond perception rule: two atoms are
    considered to be bonded when their distance is smaller than the sum of their
    covalent radii plus a tolerance value [3]_. Use with care.

    .. [3] E. C. Meng and R. A. Lewis, *Determination of molecular topology and atomic
       hybridization states from heavy atom coordinates*, J. Comp. Chem. **12**, 891-898
       (1991).
    """

    n = len(atomicnums)

    assert coordinates.shape == (n, 3)

    A = np.zeros((n, n))

    for i in range(n):
        r_i = qcel.covalentradii.get(atomicnums[i], units="angstrom")

        for j in range(i + 1, n):
            r_j = qcel.covalentradii.get(atomicnums[i], units="angstrom")

            distance = np.sqrt(np.sum((coordinates[i] - coordinates[j]) ** 2))

            if distance < (r_i + r_j + connectivity_tolerance):
                A[i, j] = A[j, i] = 1

    return A


def match_graphs(G1: nx.Graph, G2: nx.Graph) -> List[Dict[Any, Any]]:
    """
    Compute RMSD using the quaternion polynomial method

    Parameters
    ----------
    G1: networkx.Graph
        Graph 1
    G2: networkx.Graph
        Graph 2

    Returns
    -------
    List[Dict[Any, Any]]
        All possible mappings between nodes of graph 1 and graph 2 (isomorphisms)

    Raises
    ------
    ValueError
        If the graphs `G1` and `G2` are not isomorphic
    """

    GM = nx.algorithms.isomorphism.GraphMatcher(G1, G2)

    # Check if graphs are actually isomorphic
    if not GM.is_isomorphic():
        # TODO: Create a new exception
        raise ValueError(f"Graphs {G1} and {G2} are not isomorphic.")

    # Extract all isomorphisms in a list
    return [isomorphism for isomorphism in GM.isomorphisms_iter()]