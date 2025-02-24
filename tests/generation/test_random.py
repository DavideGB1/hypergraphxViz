import pytest
import random
from hypergraphx.generation.random import random_shuffle, random_shuffle_all_orders
from hypergraphx import Hypergraph


@pytest.fixture
def dummy_hypergraph():
    edges = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    return Hypergraph(edges)


def test_no_shuffle(dummy_hypergraph):
    """Test that with p=0, the hypergraph remains unchanged."""
    random.seed(42)
    hg = dummy_hypergraph
    original_edges = list(hg.get_edges(3))
    random_shuffle(hg, size=3, inplace=True, p=0.0)
    new_edges = list(hg.get_edges(3))
    assert (
        new_edges == original_edges
    ), f"Expected edges unchanged for p=0, got {new_edges}"


def test_full_shuffle():
    """Test that with p=1, all hyperedges are replaced.

    Using a fresh instance here to ensure no interference from other tests.
    """
    random.seed(42)
    edges = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    hg = Hypergraph(edges)
    original_edges = list(hg.get_edges(size=3))
    random_shuffle(hg, size=3, inplace=True, p=1.0)
    new_edges = list(hg.get_edges(size=3))
    # With p=1.0, all edges should be replaced with new random ones.
    assert (
        new_edges != original_edges
    ), f"Expected edges shuffled for p=1, got {new_edges}"
    assert len(new_edges) == len(
        original_edges
    ), "Number of edges should remain the same"


def test_intermediate_shuffle():
    """Test that with p=0.5, exactly half of the hyperedges are replaced.

    Using a fresh instance to ensure no interference from other tests.
    """
    import random

    random.seed(42)
    edges = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (3, 4, 7)]
    hg = Hypergraph(edges)
    original_edges = list(hg.get_edges(size=3))

    p = 0.5
    random_shuffle(hg, size=3, inplace=True, p=p)
    new_edges = list(hg.get_edges(size=3))

    # Ensure the number of edges remains the same.
    assert len(new_edges) == len(
        original_edges
    ), "Number of edges should remain the same"

    # Count how many hyperedges were replaced.
    num_replaced = sum(1 for orig, new in zip(original_edges, new_edges) if orig != new)
    expected_replacements = int(p * len(original_edges))

    assert (
        num_replaced == expected_replacements
    ), f"Expected {expected_replacements} hyperedges replaced, got {num_replaced}"


def test_intermediate_shuffle_only_one_size():
    """Test that with p=0.5, exactly half of the hyperedges are replaced.

    Using a fresh instance to ensure no interference from other tests.
    """
    import random

    random.seed(42)
    edges = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (3, 4, 7), (1, 2), (3, 4), (5, 6)]
    hg = Hypergraph(edges)
    original_edges = list(hg.get_edges(size=3))

    p = 0.5
    random_shuffle(hg, size=3, inplace=True, p=p)
    new_edges = list(hg.get_edges(size=3))
    total_new_edges = list(hg.get_edges())

    # Count how many hyperedges were replaced.
    num_replaced = sum(1 for orig, new in zip(original_edges, new_edges) if orig != new)
    expected_replacements = int(p * len(original_edges))

    # Ensure edges of size 2 are still the same
    assert (1, 2) in total_new_edges
    assert (3, 4) in total_new_edges
    assert (5, 6) in total_new_edges

    # Ensure around p * len(original_edges) edges are replaced
    assert (
        num_replaced == expected_replacements
    ), f"Expected {expected_replacements} hyperedges replaced, got {num_replaced}"


def test_non_inplace(dummy_hypergraph):
    """Test that non-inplace operation returns a new hypergraph while leaving the original unchanged."""
    random.seed(42)
    hg = dummy_hypergraph
    original_edges = list(hg.get_edges(size=3))
    new_hg = random_shuffle(hg, size=3, inplace=False, p=1.0)
    # Original hypergraph should remain unchanged.
    assert (
        list(hg.get_edges(size=3)) == original_edges
    ), "Original hypergraph should remain unchanged in non-inplace mode"
    # The new hypergraph should have different edges.
    assert (
        list(new_hg.get_edges(size=3)) != original_edges
    ), "New hypergraph should have shuffled edges"


def test_both_order_and_size_error(dummy_hypergraph):
    """Test that specifying both order and size raises a ValueError."""
    hg = dummy_hypergraph
    with pytest.raises(ValueError, match="both specified"):
        random_shuffle(hg, order=2, size=3, inplace=True, p=1.0)


def test_neither_order_nor_size_error(dummy_hypergraph):
    """Test that specifying neither order nor size raises a ValueError."""
    hg = dummy_hypergraph
    with pytest.raises(ValueError, match="must be specified"):
        random_shuffle(hg, inplace=True, p=1.0)


def test_invalid_p_error(dummy_hypergraph):
    """Test that an invalid value of p raises a ValueError."""
    hg = dummy_hypergraph
    with pytest.raises(ValueError, match="p must be between 0 and 1"):
        random_shuffle(hg, size=3, inplace=True, p=1.5)


def test_random_shuffle_all_orders_multiple_sizes():
    """
    Test that random_shuffle_all_orders shuffles hyperedges correctly across multiple hyperedge sizes.

    For each hyperedge size present in the hypergraph, exactly a fraction `p` of the hyperedges
    should be replaced. The test uses a fixed random seed to ensure reproducibility.
    """
    import random

    random.seed(60)

    # Define a hypergraph with hyperedges of multiple sizes.
    edges = [
        (0, 1, 2),  # size 3
        (2, 4, 5),  # size 3
        (3, 7, 8),  # size 3
        (3, 4, 7),  # size 3
        (9, 10),  # size 2
        (11, 12),  # size 2
        (13, 6),  # size 2
        (1, 2),  # size 2
        (3, 4),  # size 2
        (5, 6),  # size 2
        (12, 13, 4, 5),  # size 4
        (0, 1, 2, 3),  # size 4
        (0, 10, 12, 14),  # size 4
        (9, 11, 6, 15),  # size 4
    ]
    hg = Hypergraph(edges)

    # Record the original hyperedges for each hyperedge size.
    original_edges_by_size = {}
    for size in set(hg.get_sizes()):
        original_edges_by_size[size] = list(hg.get_edges(size=size))

    p = 0.5
    # Apply shuffling across all hyperedge sizes.
    random_shuffle_all_orders(hg, p=p, inplace=True)

    # Verify that for each hyperedge size, the number of replaced hyperedges is as expected.
    for size, orig_edges in original_edges_by_size.items():
        new_edges = list(hg.get_edges(size=size))
        print(new_edges)
        # Count hyperedges that have been altered.
        num_replaced = 0
        for orig, new in zip(orig_edges, new_edges):
            print(orig, new)
            if orig != new:
                num_replaced += 1
        expected_replacements = int(p * len(orig_edges))
        assert (
            num_replaced == expected_replacements
        ), f"For hyperedges of size {size}: expected {expected_replacements} replacements, got {num_replaced}."
