import matplotlib.pyplot as plt
import seaborn as sns


def _sort_for_visualization(motifs: list):
    """
    Sort motifs for visualization.
    Motifs are sorted in such a way to show first lower order motifs, then higher order motifs.

    Parameters
    ----------
    motifs : list
        List of motifs to sort

    Returns
    -------
    list
        Sorted list of motifs
    """
    import numpy as np

    motifs = np.roll(motifs, 3)
    return motifs


def plot_motifs(motifs: list, title: str = "Motifs", save_name: str = None, ax = None):
    """
    Plot motifs. Motifs are sorted in such a way to show first lower order motifs, then higher order motifs.

    Parameters
    ----------
    motifs : list
        List of motifs to plot

    save_name : str, optional
        Name of the file to save the plot, by default None

    Raises
    ------
    ValueError
        Motifs must be a list of length 6.

    Returns
    -------
    None
    """
    if len(motifs) != 6:
        raise ValueError("Motifs must be a list of length 6.")
    if ax is None:
        fig, ax = plt.subplots()
    motifs = _sort_for_visualization(motifs)
    cols = ["#cd3031" if (x < 0) else "#557fa3" for x in motifs]
    g = sns.barplot(x=["I", "II", "III", "IV", "V", "VI"], y=motifs, palette=cols, hue = ["I", "II", "III", "IV", "V", "VI"], legend=False, ax = ax)
    g.axhline(0, color="black", linewidth=0.5)
    ax.set_ylim(-1, 1)
    ax.set_ylabel("Motif abundance score")
    sns.despine()
    ax.set_title(title)
    if save_name != None:
        plt.savefig("{}".format(save_name), bbox_inches="tight")
