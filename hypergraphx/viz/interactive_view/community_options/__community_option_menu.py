import random


class CommunityOptionsDict(dict):
    def __init__(self):
        super().__init__()
        self.dictionary = dict()
        self["number_communities"] = 2
        self["realizations"] = 10
        self["seed"] = random.randint(0,10000)
        self["max_iterations"] = 500
        self["check_convergence_every"] = 1
        self["normalizeU"] = True
        self["baseline_r0"] = False
        self["assortative"] = True
    def update(self, dictionary, **kwargs):
        for (k,v) in dictionary.items():
            try:
                self[k] = dictionary[k]
            except KeyError:
                pass

