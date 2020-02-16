import graph_tool as gt
import numpy as np
import pytest

from spyrmsd import graph, io, molecule
from tests import molecules


@pytest.mark.parametrize(
    "mol, n_bonds",
    [(molecules.benzene, 12), (molecules.ethanol, 8), (molecules.dialanine, 22)],
)
def test_adjacency_matrix_from_atomic_coordinates(
    mol: molecule.Molecule, n_bonds: int
) -> None:

    A = graph.adjacency_matrix_from_atomic_coordinates(mol.atomicnums, mol.coordinates)

    G = graph.graph_from_adjacency_matrix(A)

    assert G.num_vertices() == len(mol)
    assert G.num_edges() == n_bonds

@pytest.mark.parametrize("mol", molecules.allobmolecules)
def test_adjacency_matrix_from_mol(mol) -> None:

    natoms = io.numatoms(mol)
    nbonds = io.numbonds(mol)

    A = io.adjacency_matrix(mol)

    assert A.shape == (natoms, natoms)
    assert np.alltrue(A == A.T)
    assert np.sum(A) == nbonds * 2

    for i, j in io.bonds(mol):

        assert A[i, j] == 1

@pytest.mark.parametrize("mol", molecules.allobmolecules)
def test_graph_from_adjacency_matrix(mol) -> None:

    natoms = io.numatoms(mol)
    nbonds = io.numbonds(mol)

    A = io.adjacency_matrix(mol)

    assert A.shape == (natoms, natoms)
    assert np.alltrue(A == A.T)
    assert np.sum(A) == nbonds * 2

    G = graph.graph_from_adjacency_matrix(A)

    assert G.num_vertices() == natoms
    assert G.num_edges() == nbonds

@pytest.mark.parametrize(
    "rawmol, mol", zip(molecules.allobmolecules, molecules.allmolecules)
)
def test_graph_from_adjacency_matrix_atomicnums(rawmol, mol) -> None:

    natoms = io.numatoms(rawmol)
    nbonds = io.numbonds(rawmol)

    A = io.adjacency_matrix(rawmol)

    assert len(mol) == natoms
    assert mol.adjacency_matrix.shape == (natoms, natoms)
    assert np.alltrue(mol.adjacency_matrix == A)
    assert np.sum(mol.adjacency_matrix) == nbonds * 2

    G = mol.to_graph()

    assert G.num_vertices() == natoms
    assert G.num_edges() == nbonds

    for idx, atomicnum in enumerate(mol.atomicnums):
        assert G.vertex_properties["atomicnum"][idx] == atomicnum

from graph_tool.all import *

@pytest.mark.parametrize(
    "G1, G2",
    [
        *[(lattice((n,n)), lattice((n,n))) for n in range(2, 5)],
        *[(circular_graph(n), circular_graph(n)) for n in range(1, 5)],
    ],
)
def test_match_graphs_isomorphic(G1: gt.Graph, G2: gt.Graph) -> None:

    with pytest.warns(UserWarning):
        isomorphisms = graph.match_graphs(G1, G2)

    assert len(isomorphisms) != 0

@pytest.mark.parametrize(
    "G1, G2",
    [
        *[(lattice((n,n)), lattice((n+1,n))) for n in range(2, 5)],
        *[(circular_graph(n), circular_graph(n + 1)) for n in range(1, 5)],
    ],
)
def test_match_graphs_not_isomorphic(G1, G2) -> None:

    with pytest.raises(ValueError), pytest.warns(UserWarning):
        graph.match_graphs(G1, G2)