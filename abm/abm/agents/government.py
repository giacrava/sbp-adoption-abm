# -*- coding: utf-8 -*-


import mesa


class Government(mesa.Agent):
    """
    Class responsible to report the payments offered to adopt SBP.

    Attributes
    ----------
    sbp_payments : pd Series
        Payment offered to adopt SBP for each year

    Methods
    ----------
    retrieve_payments
        Retrieve the payment offered to adopt SBP in a specific year.

    """

    def __init__(self, unique_id, model, sbp_payments):
        """
        Parameters
        ----------
        sbp_payments : pandas Series
            Payment offered to adopt SBP for each year

        """

        super().__init__(unique_id, model)
        self._sbp_payments = sbp_payments

    @property
    def sbp_payments(self):
        return self._sbp_payments

    def retrieve_payments(self, year):
        """
        Method to retrieve the payment offered to adopt SBP in a specific year.

        Parameters
        ----------
        year : int
            Year for which the payment want to be retrieved

        Raises
        ------
        KeyError
            Raised if no data is available for the requested year

        Returns
        ------
        int
            Payment offered in the requested year in €/hectare

        """
        try:
            return self.sbp_payments.loc[year, 'sbp_payment']
        except KeyError:
            raise KeyError('Payment for ' + str(year) + ' not available.'
                           'Year outside the time span of the model.')
