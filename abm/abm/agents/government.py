# -*- coding: utf-8 -*-


import mesa


class Government(mesa.Agent):
    """
    Class responsible to report the payments offered to adopt SBP.

    Attributes
    ----------
    sbp_payments : pd Series
        Payment offered to adopt SBP for each year

    municipalities_pcf : list
        List of municipalities to which payments are offered during the PCF
        project

    Methods
    ----------
    retrieve_payments
        Retrieve the payment offered to adopt SBP in a specific year.

    """

    def __init__(self, unique_id, model, sbp_payments, municipalities_pcf):
        """
        Parameters
        ----------
        sbp_payments : pandas Series
            Payment offered to adopt SBP for each year
            
        municipalities_pcf : set
            List of names of the municipalities involved in the PCF project,
            where payments were offered

        """

        super().__init__(unique_id, model)
        self._sbp_payments = sbp_payments
        self._municipalities_pcf = set(municipalities_pcf)

    @property
    def sbp_payments(self):
        return self._sbp_payments

    @property
    def municipalities_pcf(self):
        return self._municipalities_pcf

    def retrieve_payments(self, year, munic):
        """
        Method to retrieve the payment offered to adopt SBP in a specific year
        and in the specific municipality.

        Checks if municipality receives payment during PCF project. If not,
        payment set to 0. If yes, read value of the payment for the
        corresponding year.

        Parameters
        ----------
        year : int
            Year for which the payment want to be retrieved

        munic : str
            Name of the municipality for which to retrieve payments

        Raises
        ------
        KeyError
            Raised if no data is available for the requested year

        Returns
        ------
        int
            Payment offered in the requested year in €/hectare

        """
        if munic not in self.municipalities_pcf:
            return 0.0
        else:
            try:
                return self.sbp_payments.loc[year, 'sbp_payment']
            except KeyError:
                raise KeyError('Payment for ' + str(year) + ' not available.'
                               'Year outside the time span of the model.')
