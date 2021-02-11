import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from scipy.interpolate import interp1d
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from scipy import interpolate
from scipy.stats import norm
from joblib import Parallel, delayed
import networkx as nx
from scipy.stats import norm
import scipy as sp
import matplotlib.pyplot as plt


class bootstrap():
    def __init__(self, df_swap):
        """Initialization of bootstrap function. Arguments passed are
           df_swap = dataframe with as index maturities and as column the swaprates"""
        # Make empty df for zerocurve
        zerocurve = pd.DataFrame({'Years':[1],'Zero rate':df_swap.swaprate.iloc[0]})
        zerocurve = zerocurve.set_index('Years')
        # All unknowns are set to nan values to fill with bootstrapping later
        for i in np.arange(2,21,1):
            zerocurve.loc[i] = np.nan
        # Save as attributes to reuse later
        self.zerocurve = zerocurve
        self.df_swap = df_swap

    def bootstrap(self,disc_rates, disc_rates_times,swaprate, duration):
        """Takes known discounting rates and known swap rate for some times
        and returns the swaprate for an unknown time"""
        # payterm = years between payments
        # discount rates = libor/ois like rates
        # swaprate is the at-par rate for the IRS
        # duration is the number of years of the swap
        
        # We loop through all payments except for the unknown
        swapvalue = 0
        for i,time in enumerate(disc_rates_times):
            if time != duration: # intermediate payouts, for which we know the coupon, namely the swaprate
                payout = swaprate # percentage, so is dollar amount given base of 100
            depreciation = (1+disc_rates[i]/100)**(time)
            swapvalue += (payout / depreciation)
        # We know that swapvalue + (coupon+100)/(1+r)^T=100 so we can solve for r
        rate = ((100+swaprate)/(100-swapvalue))**(1/duration)-1
        return rate*100


    def get_zerocurve(self):
        """Using knowledge of all swaps and 1-year discount rate we can
           estimate all zero rates in this function."""
        zerocurve = self.zerocurve
        swaprates = self.df_swap
        for years,row in zerocurve.iterrows():
            if (np.isnan(row['Zero rate'])):
                # Unknown rate, so we need to bootstrap!
                # Obtain swap rate for this maturity
                swaprate = swaprates.loc[years].swaprate
                known_rates = zerocurve.loc[:years-1]
                zerorate = self.bootstrap(known_rates.values,known_rates.index,swaprate,years)
                zerocurve.loc[years] = zerorate
        return zerocurve

    def merge(self, MJ_values):
        zerocurve = self.get_zerocurve()
        df = pd.merge(zerocurve, MJ_values, left_index=True, right_index=True, how='left')
        df['diff'] = df['Zero rate'] - df['zerorate']
        df = df.fillna('-')
        return df