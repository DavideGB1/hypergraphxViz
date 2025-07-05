import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from hypergraphx import Hypergraph
from hypergraphx.readwrite import load_hypergraph


def distr_bin(data, n_bin=30, logbin=True):
    """
    Performs logarithmic or linear binning of raw data.
    This is a helper function for calculating distributions.
    """
    if len(data) == 0:
        # Return empty tuples if there is no data to avoid errors
        return (), ()

    min_d = float(min(data))
    if logbin and min_d <= 0:
        print(f"Warning: Non-positive data for log-binning. Min value: {min_d}. Skipping.")
        return (), ()

    n_bin_float = float(n_bin)
    bins = np.arange(n_bin_float + 1)

    if logbin:
        # Avoid division by zero if min_d is 1
        data_norm = np.array(data) / min_d if min_d != 1 else np.array(data)

        # Avoid math error if max value is 1
        max_data = float(max(data_norm))
        base = np.power(max_data, 1.0 / n_bin_float) if max_data > 1.0 else 1.1

        bins = np.power(base, bins)
        bins = np.ceil(bins)
    else:
        data_norm = np.array(data)
        min_data, max_data = float(min(data_norm)), float(max(data_norm))
        if max_data == min_data:
            # If all data points are the same, binning is not possible
            return (np.array([min_data]), np.array([1.0]))
        delta = (max_data - min_data) / n_bin_float
        bins = bins * delta + min_data

    hist, bin_edges = np.histogram(data, bins=bins)

    ii = np.nonzero(hist)[0]
    if len(ii) == 0:
        return (), ()

    hist = hist[ii]
    # Calculate the center of the bins where the histogram is non-zero
    bin_centers = (bin_edges[ii] + bin_edges[ii + 1]) / 2.0

    # Normalize the frequency
    frequency = hist / float(sum(hist))

    return bin_centers, frequency


# =============================================================================
# 2. COMPUTATION FUNCTION
# =============================================================================

def compute_binned_degree_distributions(h: Hypergraph) -> dict:
    """
    Calculates the binned degree distributions for each hyperedge size.

    Args:
        h (Hypergraph): The hypergraph to analyze.

    Returns:
        dict: A dictionary where keys are the hyperedge sizes
              and values are tuples of (bins, frequency).
    """
    results = {}
    for size in range(2, h.max_size() + 1):
        # Determine binning parameters based on the hyperedge size
        logbin = (size != 2)
        n_bin = 8 if size == 2 else 10

        # Extract and filter degrees
        degrees = list(h.degree_sequence(size=size).values())
        degrees = [d for d in degrees if d > 0]

        # If there are no nodes with degree > 0 for this size, skip
        if not degrees:
            continue

        # Calculate bins and frequencies
        bins, frequency = distr_bin(degrees, n_bin=n_bin, logbin=logbin)

        # Store the results only if binning produced a valid output
        if len(bins) > 0 and len(frequency) > 0:
            results[size] = (bins, frequency)

    return results


# =============================================================================
# 3. PLOTTING FUNCTION
# =============================================================================

def draw_degree_distribution_plot(processed_data: dict, ax: plt.Axes, color_dict: dict = None,
                                  hye_facecolor: dict = None):
    """
    Draws a scatter plot of degree distributions on a given axis.

    Args:
        processed_data (dict): Pre-calculated data from the `compute_binned_degree_distributions` function.
        ax (plt.Axes): The Matplotlib axis to draw on.
        color_dict (dict, optional): Dictionary mapping size to point color.
        hye_facecolor (dict, optional): Dictionary mapping size to point edgecolor.
    """
    # Set default colors if not provided
    if color_dict is None:
        color_dict = {2: "#FCB07E", 3: "#048BA8", 4: "#99C24D", 5: "#BC2C1A", 6: "#2F1847"}
    if hye_facecolor is None:
        hye_facecolor = color_dict  # Use the same colors for face and edge by default

    # Plot the data for each size
    for size, (bins, frequency) in processed_data.items():
        color = color_dict.get(size, "#808080")  # Default to gray for unmapped sizes
        edge_color = hye_facecolor.get(size, "#333333")

        ax.scatter(
            bins,
            frequency,
            alpha=0.9,
            label=f"Size: {size}",
            s=150,
            c=color,
            edgecolors=edge_color
        )

    # Final plot settings
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Higher-order degree (k)")
    ax.set_ylabel("Frequency P(k)")
    ax.set_title("Degree Distribution in Orders")
    ax.legend(frameon=False, loc='lower left')
    sns.despine(ax=ax)


# =============================================================================
# 4. WRAPPER FUNCTION (Main user interface)
# =============================================================================

def plot_degree_distribution_for_orders(h: Hypergraph, color_dict=None, hye_facecolor=None, ax=None):
    """
    Calculates and plots the degree distribution for different orders of a hypergraph.

    This function acts as a wrapper, combining computation and plotting for ease of use.

    Args:
        h (Hypergraph): The input hypergraph.
        color_dict (dict, optional): Map from size to color for the points.
        hye_facecolor (dict, optional): Map from size to color for the point edges.
        ax (plt.Axes, optional): The axis to plot on. If None, a new one is created.

    Returns:
        plt.Axes: The Matplotlib axis with the plot.
    """
    # If no axis is provided, create a new one
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    # 1. Computation step: get the binned data
    processed_data = compute_binned_degree_distributions(h)

    # 2. Drawing step: pass the data to the plotting function
    draw_degree_distribution_plot(processed_data, ax, color_dict, hye_facecolor)

    return ax