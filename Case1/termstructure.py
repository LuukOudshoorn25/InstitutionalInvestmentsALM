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

    def forward_rate(self,t1=19,t2=20):
        """Calculate the forward rate from two spot rates and two times"""
        # Obtain discount factors
        zerocurve = self.get_zerocurve()
        r1 = zerocurve.loc[t1]
        r2 = zerocurve.loc[t2]
        discount1 = (1+r1.iloc[0]/100)**t1
        discount2 = (1+r2.iloc[0]/100)**t2
        
        f12 = (discount2/discount1)-1
        f12 = f12*100
        return f12

    def UFR_zerocurve(self):
        """Extend using a fixed number for the one-year forward rate the zerocurve up to 60 years"""
        # Get UFR rate
        UFR = self.forward_rate(19,20)/100
        # Get zerocurve
        zerocurve = self.get_zerocurve()
        # From 20 years onward, we consider the UFR as forward rate for each consecutive year
        # Add elements to zerocurve
        for year in range(21,61):
            new_rate = ((UFR+1)*(1+zerocurve.loc[year-1]/100)**(year-1))**(1/year)-1
            zerocurve.loc[year] = new_rate*100
        return zerocurve
    
    def UFR_forward(self):
        """Obtain the UFR curve using the convergence equation"""
        # Get zerocurve
        zerocurve = self.get_zerocurve()
        # Get forward rates for the known data
        f_UFR = pd.DataFrame({'h':[], 'URF_forward':[]}).set_index('h')
        #for year in range(1,len(zerocurve)+1):
        #    frate = self.forward_rate(t1=1, t2=year)
        #    f_UFR.loc[year] = frate
        # Define out-of-sample function
        B = lambda h: (1-np.exp(-0.5*h))/(0.5*h)
        f = lambda x,h: 4.2+(x-4.2)*B(h)            
        f_19_20 = self.forward_rate(19,20)
        
        for h in range(1,60):
            f_UFR.loc[h] = f(f_19_20,h)
        return f_UFR


