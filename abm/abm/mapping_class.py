# -*- coding: utf-8 -*-


import pandas as pd


class Mappings:
    """
    Class storing all the identificative string - object mappings. This is
    needed to avoid errors for the visualization making all the objects JSON
    serializable. It is used to access the objects from the relative strings.

    Attributes
    ----------

    envronments : pd Series
        Links each Municipality object (the values) to a string representing
        their name (the keys)

    """

    def __init__(self):

        self.environments = pd.Series()


mappings = Mappings()
