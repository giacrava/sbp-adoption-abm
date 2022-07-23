# -*- coding: utf-8 -*-


import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class TransformAdoptionFeatures(BaseEstimator, TransformerMixin):

    def __init__(self,
                 keep_adoption_in_port=True,
                 add_square_cumul_adoption=False):
        self.keep_adoption_in_port = keep_adoption_in_port
        self.add_square_cumul_adoption = add_square_cumul_adoption

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        feats_to_keep = ["tot_cumul_adoption_pr_y_munic"]
        if self.keep_adoption_in_port:
            feats_to_keep.append("tot_cumul_adoption_pr_y_port")

        if self.add_square_cumul_adoption:
            col_to_add = (X['tot_cumul_adoption_pr_y_munic']
                          * X['tot_cumul_adoption_pr_y_munic'])
            col_to_add.name = 'tot_cumul_adoption_pr_y_munic_squared'
            return pd.concat([X[feats_to_keep], col_to_add], axis=1)
        else:
            return X[feats_to_keep]

class TransformCensusFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        feats_to_keep = ['pastures_area_var', 'pastures_area_mean',
                         'educ_second_super', 'farmers_over65',
                         'inc_mainly_ext', 'educ_none', 'work_unit_100ha',
                         'agric_area_owned', 'lu_per_agric_area']
        XX = X[feats_to_keep]

        return XX


class TransformClimateFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        climate_features = X.columns

        feats_mean_t = [feat for feat in climate_features
                        if 'av_d_mean_t_average' in feat]
        feats_max_t = [feat for feat in climate_features
                       if 'av_d_max_t_average' in feat]
        feats_prec = [feat for feat in climate_features
                      if 'cons_days_no_prec_average' in feat]

        feats_to_keep = feats_mean_t + feats_max_t + feats_prec

        return X[feats_to_keep]


class TransformSoilFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        soil_features = X.columns

        feats_to_keep = [feat for feat in soil_features
                         if feat != 'pH_mean_munic']

        return X[feats_to_keep]


class TransformEconomicFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        # Nothing to do, it's just sbp_payments and we pass it
        return X
