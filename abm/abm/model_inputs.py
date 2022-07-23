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
    
ml_dataset : str
    Path to the dataset needed to train the ML models during the instantiation
    of the ABM

"""

sbp_payments_path = (pathlib.Path(__file__).parent.parent / 'data'
                     / 'sbp_payments.xlsx')

clsf_folder_path = (pathlib.Path(__file__).parent.parent / 'ml_model'
                    / 'classifier')

regr_folder_path = (pathlib.Path(__file__).parent.parent / 'ml_model'
                    / 'regressor')

ml_dataset = (pathlib.Path(__file__).parent.parent
              / 'Municipalities final dataset for analysis.csv')
