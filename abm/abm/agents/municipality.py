# -*- coding: utf-8 -*-


import pandas as pd

from mesa_geo.geoagent import GeoAgent

from ..mapping_class import mappings


class Municipality(GeoAgent):
    """
    Class for the main agents of the simulation, estimating the adoption of
    SBP.

    Attributes
    ----------
    Municipality : str
        Name of the municipality
    District : str
        Name of the district which the municipality is part of
    census_data : dict
        Variables for the municipality obtained from the census, for each year
        from 1995 to 2019
    perm_pastures_ha : dict
        Area of permanent pastures in hectare in the municipality, for each
        year from 1995 to 2019
    perm_pastures_ref : float
        Area of permanent pastures in hectare in the municipality in 2009, used
        as reference for all the other variables regarding adoption
    yearly_adoption : dict
        Adoption of SBP in the municipality in each past year divided by the
        permanent pastures area of the municipality
    yearly_adoption_ha : dict
        Adoption of SBP in the municipality in each past year in hectares
    cumul_adoption_tot : dict
        Adoption of SBP in the municipality over all previous years, divided by
        the permanent pastures area of the municipality
    cumul_adoption_tot_ha : float
        Adoption of SBP in the municipality over all previous years in hectares

    Methods
    ----------
    get_neighbors
        Retrieve the names of the neighboring Municipality objects

    """

    def __init__(self, unique_id, model, shape):
        """
        Initialize a Municipality agent.

        """
        super().__init__(unique_id, model, shape)

        # Attributes set by the Agent Creator from the Shapefile during the
        # initialization
        self.Municipality = ""
        self.District = ""

        # Attributes set during initialization of the municipalities
        self.census_data = None
        self.perm_pastures_ha = None
        self.perm_pastures_ref = None

        self.yearly_adoption = None
        self.yearly_adoption_ha = None

        self.cumul_adoption_tot = None
        self.cumul_adoption_tot_ha = None

        # Attributes used to save state before running advance method
        self._adoption_in_year = None

    def set_tot_cumul_adoption(self):
        """
        Called by the model during instantiation of Municipalities.

        Calculate the total adoption over all the previous years relative to
        the permanent pastures area in 2009 and set the
        cumul_adoption_tot attribute.

        Returns
        -------
        None.

        """
        self.cumul_adoption_tot = sum(self.yearly_adoption.values())

    def step(self):
        """
        Step method called by the step method of the model.

        If the municipality has a pastures area of 0 in the year or in the
        previous one, or already adopted all its pastures area,
        the adoption in the year is set to 0. Otherwise,
        it retrieves all the data and pass them in the right order to the ML
        model to predict the fraction of permanent pastures area in the
        municipality in which SBP is adopted in the year, storing it in a
        temporary attribute.

        Returns
        -------
        None.

        """
        if (self.perm_pastures_ha[self.model.year] == 0 or
                self.perm_pastures_ha[self.model.year - 1] == 0):
            self._adoption_in_year = 0
        elif (self.cumul_adoption_tot_ha >=
                self.perm_pastures_ha[self.model.year]):
            self._adoption_in_year = 0
        else:
            ml_clsf_input_data = self._retrieve_data(self.model.ml_clsf_feats,
                                                     self.model.year,
                                                     'clsf')
            ml_regr_input_data = self._retrieve_data(self.model.ml_regr_feats,
                                                     self.model.year,
                                                     'regr')
            self.estimate_adoption(self.model.ml_clsf, ml_clsf_input_data,
                                   self.model.ml_regr, ml_regr_input_data)

    def _retrieve_data(self, features, year, estimator):
        """
        Method to return all the data that need to be passed to the ML models
        to estimate the SBP adoption in the year.

        Parameters
        ----------
        features : list
            List of strings reporting the name of the features used to train
            the machine learning model, in the order they were used to train it
        year : int
            Year of the current model timestep
        estimator : string
            "clsf" or "regr", required to retrieve the payment feature in case
            collecting data for the regressor

        Raises
        ------
        ValueError
            Raised if some features to be input to the machine learning model
            are missing.

        Returns
        -------
        attributes : pd Series
            Contains all the attributes required by the machine learning model
            to predict adoption.

        """
        attributes = pd.Series(index=features)

        # Adoption
        if "tot_cumul_adoption_pr_y_munic" in attributes.index:
            attributes["tot_cumul_adoption_pr_y_munic"] = (
                self.cumul_adoption_tot
                )
        if "tot_cumul_adoption_pr_y_port" in attributes.index:
            attributes["tot_cumul_adoption_pr_y_port"] = (
                self.model.cumul_adoption_tot_port
                )

        # Other
        attributes.update(self.census_data[self.model.year - 1])
        if estimator == 'regr':
            attributes['sbp_payment'] = (
                self.model.government.retrieve_payments(year)
                    )
        environment = mappings.environments[self.Municipality]
        attributes.update(environment.average_climate)
        attributes.update(environment.soil)

        if attributes.isnull().any():
            missing_attr = attributes[attributes.isnull()].index.tolist()
            raise ValueError("The following attributes to input to the machine"
                             " learning model are missing: "
                             + ", ".join(missing_attr))
        
        return attributes.to_frame().T

    def estimate_adoption(self, classifier, input_clsf, regressor, input_regr):
        """
        Method to estimate the area of SBP installed in the municipality.

        It uses the classifier to estimate the probability
        of having SBP adoption and generates a random number between 0 and 1
        to decide if there is adoption stochastically. If there is, it uses the
        regressor to estimate the area switched to SBP and set a temporary
        variable to the value estimated. If there is no adoption or the
        adoption estimated is negative, it sets the temporary variable to 0.

        Returns
        -------
        None

        """
        prob_adopt = classifier.predict_proba(input_clsf)[0][1]
        if self.model.random.uniform(0, 1) < prob_adopt:
            adoption = regressor.predict(input_regr)
            adoption_ha = adoption * self.perm_pastures_ref
            if adoption < 0:
                self._adoption_in_year = 0
            elif ((self.cumul_adoption_tot_ha + adoption_ha)
                  > self.perm_pastures_ha[self.model.year]):
                adoption_ha = (self.perm_pastures_ha[self.model.year]
                               - self.cumul_adoption_tot_ha)
                self._adoption_in_year = adoption_ha / self.perm_pastures_ref
            else:
                self._adoption_in_year = adoption[0]
        else:
            self._adoption_in_year = 0

    def advance(self):
        """
        Advance method called by the step of the model after the step() method
        of all municipalities are called.

        Updates all the attributes regarding adoption according the
        estimation for the current year.
        Sums the hectares adopted to the total adoption in Portugal in the
        current year.

        Returns
        -------
        None.

        """
        year = self.model.year

        self.yearly_adoption[year] = self._adoption_in_year
        self.yearly_adoption_ha[year] = (
            self._adoption_in_year * self.perm_pastures_ref
            )
        self.cumul_adoption_tot += self._adoption_in_year
        self.cumul_adoption_tot_ha += self.yearly_adoption_ha[year]

        self.model.adoption_in_year_port_ha += self.yearly_adoption_ha[year]
