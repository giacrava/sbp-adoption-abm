# -*- coding: utf-8 -*-


class MunicipalityEnvironment:
    """
    Class responsible for reporting all the data regarding climate and soil of
    the Municipality agents.

    Attributes
    ----------
    average_climate : pandas Series
        Reports data regarding temperatures (in °C) and precicipitation sum (in
        mm / areas of 0.1° side).

    soil : pandas Series
        Reports data regardin various soil properties of the municipality.

    """

    def __init__(self,
                 munic_average_climate_data,
                 munic_soil_data):
        """
        Parameters
        ----------
        munic_average_climate : pd Series
            Series reporting the average climate of the municipality over
            the period 1995 - 2018.

        munic_soil_data : pd Series
            Series reporting soil data for the municipality.

        """
        self.average_climate = munic_average_climate_data
        self.soil = munic_soil_data
