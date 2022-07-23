# -*- coding: utf-8 -*-


from sklearn.base import BaseEstimator, TransformerMixin


class TransformCensusFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        feats_to_keep = ['pastures_area_var', 'pastures_area_mean',
                         'educ_second_super', 'farmers_over65',
                         'inc_mainly_ext', 'educ_none', 'work_unit_100ha',
                         'agric_area_owned', 'lu_cattle', 'lu_per_agric_area']
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
