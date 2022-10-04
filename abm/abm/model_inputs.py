# -*- coding: utf-8 -*-


import pathlib

"""
Inputs needed to instantiate the model.

Data
----------
sbp_payments : str
    Path to the spreadsheed with the total payment in €/hectare provided by the
    Portuguese Carbon Fund for each year.

clsf_folder_path : str
    Path to the folder where the ML classifier model and the name of its
    features are located

regr_folder_path : str
    Path to the folder where the ML regressor model and the name of its
    features are located

municipalities_pcf_path : str
    Path to the file with the list of names of the municipalities involved in
    the PCF project, where payments were offered
"""

sbp_payments_path = (pathlib.Path(__file__).parent.parent / 'data'
                     / 'sbp_payments.xlsx')

clsf_folder_path = (pathlib.Path(__file__).parent.parent / 'ml_model'
                    / 'classifier')

regr_folder_path = (pathlib.Path(__file__).parent.parent / 'ml_model'
                    / 'regressor')

municipalities_pcf_path = (pathlib.Path(__file__).parent.parent / 'data'
                           / 'municipalities_adoption_PCF.csv')
