# -*- coding: utf-8 -*-


import pandas as pd
import geopandas as gpd
import numpy as np
import os
import pathlib
import csv
import joblib

import mesa
import mesa.time
import mesa.datacollection
import mesa_geo

from . import agents
from .mapping_class import mappings
from .model_inputs import sbp_payments_path, clsf_folder_path, regr_folder_path
from .custom_transformers import (TransformCensusFeatures,
                                  TransformClimateFeatures,
                                  TransformSoilFeatures)


# Function for datacollector
def get_total_area_adopted(model):
    """
    Method to calculate the total cumulative area of SBP sown in Portugal.

    Called by the DataCollector.

    Returns
    -------
    total_area_pt : int
        Total area switched to SBP in Portugal since 1996.

    """
    total_area_pt = model.yearly_adoption_ha_port.cumsum()[model.year]
    return total_area_pt


class SBPAdoption(mesa.Model):
    """
    Model for SBP adoption.

    Attributes
    ----------
    government : Government object
        Entity resposible to report the payments to install SBP
    perm_pastures_ref_port : int
        Hectares of permanent pastures in Portugal in 2009
    yearly_adoption_ha_port : pd Series
        Hectares of SBP installed in Portugal each year from 1996
    cumul_adoption_tot_ha_port : int
        Hectares of SBP installed in Portugal from 1996
    cumul_adoption_tot_port : int
        Hectares of SBP installed in Portugal from 1996, divided by the total
        area of permanent pastures in Portugal
    """

    def __init__(self,
                 ml_clsf_folder=clsf_folder_path,
                 ml_regr_folder=regr_folder_path,
                 initial_year=1996,
                 sbp_payments_path=sbp_payments_path,
                 seed=None):
        """
        Initalization of the model.

        Parameters
        ----------
        initial_year : int
            Year in the interval 1996 - 2012 in which the simulation has to
            start (the adoption in this year will be predicted)
        sbp_payments_path : path str
            Path to the spreadsheed with the total payment in €/hectare
            provided by the Portuguese Carbon Fund for each year
        clsf_folder_path : path str
            Path to the folder where the ML classifier model and the name of
            its fatures are located
        regr_folder_path : path str
            Path to the folder where the ML regressor model and the name of its
            features are located
        seed : int
            Seed for pseudonumber generation

        """

        super().__init__()

        # Added mappings as an attribute so that once the model runs, possible
        # to extract the municipalities through their names
        self.mappings = mappings

        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa_geo.GeoSpace()

        if (initial_year < 1996):
            raise ValueError("The model cannot be initialized in a year "
                             "previous to 1996")
        else:
            self._year = initial_year

        self._ml_clsf = None
        self._ml_clsf_feats = None
        self._ml_regr = None
        self._ml_regr_feats = None
        self._upload_ml_models(ml_clsf_folder, ml_regr_folder)

        self.government = self._initialize_government(sbp_payments_path)

        self.perm_pastures_ref_port = None
        self.yearly_adoption_ha_port = None
        self.cumul_adoption_tot_ha_port = None
        self.cumul_adoption_tot_port = None
        self._initialize_municipalities_and_adoption()

        self._initialize_environments()

        # Attribute updated by the municipalities to calculate total adoption
        # in the year in Portugal
        self._adoption_in_year_port_ha = 0

        self.datacollector = mesa.datacollection.DataCollector(
            model_reporters={
                'Year': lambda m: m.year,
                'Cumulative area of SBP sown [ha]': get_total_area_adopted,
                'Yearly area of SBP sown [ha/y]': (
                    lambda m: m.yearly_adoption_ha_port[m.year]
                    )
                })

        # Section of code for visualization, to not start from 0 in the chart
        # if there was adoption in the year before
        dc_vars = self.datacollector.model_vars
        dc_vars['Year'].append(self.year - 1)
        dc_vars['Cumulative area of SBP sown [ha]'].append(
            self.yearly_adoption_ha_port.cumsum()[self.year - 1]
            )
        dc_vars['Yearly area of SBP sown [ha/y]'].append(
            self.yearly_adoption_ha_port[self.year - 1]
            )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, new_val):
        self._year = new_val

    @property
    def adoption_in_year_port_ha(self):
        return self._adoption_in_year_port_ha

    @adoption_in_year_port_ha.setter
    def adoption_in_year_port_ha(self, new_val):
        self._adoption_in_year_port_ha = new_val

    @property
    def ml_clsf(self):
        return self._ml_clsf

    @property
    def ml_clsf_feats(self):
        return self._ml_clsf_feats

    @property
    def ml_regr(self):
        return self._ml_regr

    @property
    def ml_regr_feats(self):
        return self._ml_regr_feats

    def _upload_ml_models(self, ml_clsf_folder, ml_regr_folder):
        """
        Called by the __init__ method.

        Loads the ML models and sets the relative model attributes.

        """
        self._ml_clsf = joblib.load(
            os.path.join(ml_clsf_folder, 'model.pkl')
            )
        self._ml_clsf_feats = self._retrieve_ml_features(
             os.path.join(ml_clsf_folder, 'features.csv')
             )
        clsf_dataset = np.genfromtxt(
            os.path.join(ml_clsf_folder, 'dataset.csv'), delimiter=','
            )
        clsf_labels = np.genfromtxt(
            os.path.join(ml_clsf_folder, 'labels.csv'), delimiter=','
            )
        self._ml_clsf.fit(clsf_dataset, clsf_labels)

        self._ml_regr = joblib.load(
            os.path.join(ml_regr_folder, 'model.pkl')
            )
        self._ml_regr_feats = self._retrieve_ml_features(
             os.path.join(ml_regr_folder, 'features.csv')
             )
        regr_dataset = np.genfromtxt(
            os.path.join(ml_regr_folder, 'dataset.csv'), delimiter=','
            )
        regr_labels = np.genfromtxt(
            os.path.join(ml_regr_folder, 'labels.csv'), delimiter=','
            )
        self._ml_regr.fit(regr_dataset, regr_labels)

    def _retrieve_ml_features(self, path):
        with open(path) as inputfile:
            rd = csv.reader(inputfile)
            return list(rd)[0]

    def _initialize_government(self, sbp_payments_path):
        """
        Called by the __init__ method.

        Instantiate the Government class.

        """
        sbp_payments = pd.read_excel(sbp_payments_path, index_col='Year')
        government = agents.Government(self.next_id(), self, sbp_payments)
        return government

    def _initialize_municipalities_and_adoption(self):
        """
        Called by the __init__ method.

        - Loads the shapefile of the municipalities
        - Checks that the file has no missing values
        - Instantiates the municipalities
        - Calls method to load data that need to be set as attribute of
        municipalities and set them + to set model's attributes regarding
        pastures and adoption in Portugal
        - Creates the space grid with the municipalities
        - Adds each municipality to the schedule
        - Creates the municipalities mapping dictionary

        """

        municipalities_shp_path = (pathlib.Path(__file__).parent.parent
                                   / 'data' / 'municipalities_shp'
                                   / 'shapefile_for_munic_abm.shp')
        municipalities_data = gpd.read_file(municipalities_shp_path)
        municipalities_data.rename(columns={'Municipali': 'Municipality'},
                                   inplace=True)

        data_is_null = municipalities_data.isnull()
        if data_is_null.values.any():
            munic_with_nan = municipalities_data[
                                data_is_null.any(axis=1)].index.tolist()
            raise ValueError('The municipalities dataset is missing values for'
                             ' the following municipalities: ' +
                             ', '.join(munic_with_nan))

        AC = mesa_geo.AgentCreator(agent_class=agents.Municipality,
                                   agent_kwargs={"model": self})

        municipalities = AC.from_GeoDataFrame(gdf=municipalities_data,
                                              unique_id='CCA_2')

        self._set_munic_attributes_from_data_and_adoption_in_port(
            municipalities
            )

        self.grid.add_agents(municipalities)
        for munic in municipalities:
            self.schedule.add(munic)

    def _set_munic_attributes_from_data_and_adoption_in_port(
            self,
            municipalities
            ):
        """
        Called by the _initialize_municipalities method.

        Method to load and set the attributes of each Municipality regarding
        census and adoption data.

        Transforms census data to be ready to be input to the ML models
        for both regressor and classifier.
        Restricts adoption data to the years before the intial year of the
        simulation, since the ones after will be estimated.
        Calls the method of the Municipalities to calculate the cumulative
        adoption in the previous 10 years.
        While iterating over the municipalities it also calculates the
        permanent pastures area and the yearly adoption in Portugal, setting
        the relative model variables. Then from these it calculates the
        cumulative adoption in the previous 10 years and divides these values
        for the permanent pastures area to obtain the ones used for the model.

        """
        pastures_data_path = (pathlib.Path(__file__).parent.parent
                              / 'data' / 'yearly_permanent_pastures_area.csv')
        pastures_data = pd.read_csv(pastures_data_path,
                                    index_col=['Municipality', 'Year'])

        census_data_path = (pathlib.Path(__file__).parent.parent
                            / 'data' / 'census_data_for_abm.csv')
        census_data = pd.read_csv(census_data_path,
                                  index_col=['Municipality', 'Year'])
        census_data_tr = TransformCensusFeatures().fit_transform(
                census_data
                )

        adoption_data_path = (pathlib.Path(__file__).parent.parent
                              / 'data'
                              / '% yearly SBP adoption per municipality.csv')
        adoption_data = pd.read_csv(adoption_data_path,
                                    index_col='Municipality')
        adoption_data.columns = adoption_data.columns.astype(int)
        adoption_cols_to_drop = [col for col in adoption_data.columns
                                 if col >= self._year]
        adoption_data.drop(adoption_cols_to_drop, axis=1, inplace=True)

        self.perm_pastures_ref_port = 0
        self.yearly_adoption_ha_port = pd.Series(
            0., index=np.arange(1995, self._year)
            )

        for munic in municipalities:
            munic_name = munic.Municipality
            try:
                munic.census_data = (
                    census_data_tr.loc[munic_name].to_dict(orient='index')
                    )
            except KeyError:
                print("Census data for the municipality of",
                      munic_name, "are missing.")

            munic.perm_pastures_ha = dict(
                pastures_data.loc[munic_name, 'pastures_area_munic_ha']
                )
            munic.perm_pastures_ref = munic.perm_pastures_ha[2009]

            try:
                munic_adoption_data = adoption_data.loc[munic_name]
            except KeyError:
                print("Adoption data for the municipality of",
                      munic_name, "are missing.")
            munic.yearly_adoption = dict(munic_adoption_data)
            munic.set_tot_cumul_adoption()

            yearly_adoption_ha = (
                munic_adoption_data * munic.perm_pastures_ref
                )
            munic.cumul_adoption_tot_ha = (
                munic.cumul_adoption_tot * munic.perm_pastures_ref
                )

            self.perm_pastures_ref_port += munic.perm_pastures_ref
            self.yearly_adoption_ha_port += yearly_adoption_ha
            munic.yearly_adoption_ha = dict(yearly_adoption_ha)

        self.cumul_adoption_tot_ha_port = (
            self.yearly_adoption_ha_port.sum()
            )
        self.cumul_adoption_tot_port = (
            self.cumul_adoption_tot_ha_port
            / self.perm_pastures_ref_port
            )

    def _initialize_environments(self):
        """
        Called by the __init__ method.

        - Loads climate and soil data
        - Create the mapping dictionary to match each Municipality with the
          relative MunicipalityEnvironment object

        """
        av_climate_data_path = (pathlib.Path(__file__).parent.parent
                                / 'data'
                                / 'municipalities_average_climate_final.csv')
        soil_data_path = (pathlib.Path(__file__).parent.parent
                          / 'data'
                          / 'municipalities_soil_final.csv')

        average_climate_data = pd.read_csv(av_climate_data_path,
                                           index_col=['Municipality'])
        average_climate_data_tr = TransformClimateFeatures().fit_transform(
            average_climate_data
            )
        soil_data = pd.read_csv(soil_data_path,
                                index_col=['Municipality'])
        soil_data_tr = TransformSoilFeatures().fit_transform(soil_data)

        for munic in self.schedule.agents:
            munic_name = munic.Municipality
            try:
                munic_average_climate = average_climate_data_tr.loc[munic_name]
            except KeyError:
                print("Average climate data for the municipality of",
                      munic_name, "are missing.")
            try:
                munic_soil = soil_data_tr.loc[munic_name]
            except KeyError:
                print("Soil data for the municipality of", munic_name,
                      "are missing.")

            self.mappings.environments[munic_name] = (
                agents.MunicipalityEnvironment(
                    munic_average_climate, munic_soil
                    )
                )

    # The following methods are not called during the initiation of the model

    def step(self):
        """
        Timestep of the model.

        Calls the step methods of the agents added to the schedule.
        Calls the method to update adoptions attributes regarding Portugal.

        """
        self.schedule.step()
        self._update_adoption_port()
        self.datacollector.collect(self)
        self.year += 1

    def _update_adoption_port(self):
        """
        Method called by the step() method to update all the adoption
        attributes for Portugal.

        Returns
        -------
        None.

        """
        self.yearly_adoption_ha_port[self.year] = self.adoption_in_year_port_ha
        self.cumul_adoption_tot_ha_port += self.adoption_in_year_port_ha
        self.cumul_adoption_tot_port = (
            self.cumul_adoption_tot_ha_port / self.perm_pastures_ref_port
            )

        self.adoption_in_year_port_ha = 0
