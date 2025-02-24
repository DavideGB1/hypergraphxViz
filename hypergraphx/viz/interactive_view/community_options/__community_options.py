from enum import Enum
import random
import re

class CommunityOptions:
    """
    Support class used to store the common options among the visualization functions.
    ...
    Attributes
    """
    def __init__(
            self,
            K = 2,
            seed = random.randint(0,10000000),
            n_realizations = 10,
            max_iter = 500,
            check_convergence_every = 1,
            normalizeU=False,
            baseline_r0=False,
            assortative=True,
            algorithm = "None"
    ):
        self.spinbox_K = K
        self.seed = seed
        self.spinbox_n_realizations = n_realizations
        self.spinbox_max_iter = max_iter
        self.spinbox_check_convergence_every = check_convergence_every
        self.checkbox_normalizeU = normalizeU
        self.checkbox_baseline_r0 = baseline_r0
        self.checkbox_assortative = assortative
        self.algorithm = algorithm
        self.current_options = dict()
        self.update_options()
    def get_options(self):
        return self.current_options
    def update_options(self):
        match self.algorithm:
            case "Hypergraph Spectral Clustering":
                self.current_options["seed"] = self.seed
                self.current_options["spinbox_n_realizations"] = self.spinbox_n_realizations
                self.current_options["spinbox_K"] = self.spinbox_K
            case "Hypergraph-MT":
                self.current_options["seed"] = self.seed
                self.current_options["spinbox_n_realizations"] = self.spinbox_n_realizations
                self.current_options["spinbox_K"] = self.spinbox_K
                self.current_options["spinbox_max_iter"] = self.spinbox_max_iter
                self.current_options["spinbox_check_convergence_every"] = self.spinbox_check_convergence_every
                self.current_options["checkbox_normalizeU"] = self.checkbox_normalizeU
                self.current_options["checkbox_baseline_r0"] = self.checkbox_baseline_r0
            case "Hy-MMSBM":
                self.current_options["seed"] = self.seed
                self.current_options["spinbox_n_realizations"] = self.spinbox_n_realizations
                self.current_options["spinbox_K"] = self.spinbox_K
                self.current_options["spinbox_max_iter"] = self.spinbox_max_iter
                self.current_options["checkbox_assortative"] = self.checkbox_assortative
            case _:
                self.current_options = dict()

class CommunityOptionsName(Enum):
    """
    Enum used to translate some GUI labels into normal strings
    """
    spinbox_K = "Number of Communities"
    seed = "Seed"
    spinbox_n_realizations = "Number of Realizations"
    #MT AND MMSBM
    spinbox_max_iter = "Maximum Iterations"
    #MT
    spinbox_check_convergence_every = "Check Convergence Every"
    checkbox_normalizeU = "Normalize U"
    checkbox_baseline_r0 = "Baseline R0"
    #MMSBM
    checkbox_assortative = "Assortative"