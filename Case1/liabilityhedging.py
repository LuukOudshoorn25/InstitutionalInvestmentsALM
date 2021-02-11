###############################################
###                                         ###
###      Subfile for the Instit Invest.     ###
###        and ALM Case 1 assignment        ###
###               Luuk Oudshoorn            ###
###            Willem-Jan de Voogd          ###
###                Mees Tierolf             ###
###      All quantitative  (Fin. Econ)      ###
###                                         ###
###############################################
 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class LiabHedger():
    def __init__(self, df):
        """Initialization of Liability Hedging class"""
        self.df = df

    def present_day_value(self):
        PV = 0
        for maturity, row in self.df.iterrows():
            PV += row.cashflow * (1/((1+row.zerorate/100)**maturity))
        return PV
    
    def ModDV01(self):
        """Obtain the modified DV01 by iterating over the cashflows"""
        moddv01 = 0
        contrib_df = pd.DataFrame({'Year':[],'Contribution':[]}).set_index('Year')
        for maturity, row in self.df.iterrows():
            new_value = maturity * row.cashflow / ((1+row.zerorate/100)**maturity)
            new_value = new_value / (1e4*(1+row.zerorate/100))
            moddv01 += new_value
            contrib_df.loc[maturity] = new_value
        return contrib_df, moddv01

    def ModConv(self):
        """Obtain the modified DV01 by iterating over the cashflows"""
        modconvex = 0
        contrib_df = pd.DataFrame({'Year':[],'Contribution':[]}).set_index('Year')
        for maturity, row in self.df.iterrows():
            new_value = 1e-4*(maturity**2+maturity) * row.cashflow / (((1+row.zerorate/100)**maturity)**2)
            modconvex += new_value
            contrib_df.loc[maturity] = new_value
        return contrib_df, modconvex

    def modDur(self):
        """Obtain modified duration from ModDV01 and current value of cashflows"""
        curval_cashflows = self.present_day_value()
        # Get Modified DV01 from other function
        contrib_df_dv01, moddv01 = self.ModDV01()
        contrib_df_dur = pd.DataFrame({'Year':[],'Contribution':[]}).set_index('Year')
        moddur_value = moddv01 * 1e4 / curval_cashflows
        # Calculate the effect of each individual year
        for year in contrib_df_dv01.index.values:
            # Leave out one year
            subdf = contrib_df_dv01.drop(year)
            sub_moddv01 = subdf.sum()
            # Obtain duration
            sub_dur = sub_moddv01 * 1e4 / curval_cashflows
            # NOTE: we might have to leave out the cashflow in this "jacknifing" technique as well!
            contribution = moddur_value - sub_dur #(years)
            contrib_df_dur.loc[year] = contribution
        return contrib_df_dur, moddur_value


def modDV01_swap(swaprate, zerorate):
    zerorate2  = zerorate-1e-4

    # Swap value = float minus fix

    float1 = zerorate/(1+zerorate)
    fix1 = swaprate * np.sum([1/((1+zerorate)**w) for w in range(1,31)])

    float2 = zerorate2/(1+zerorate2)
    fix2 = swaprate * np.sum([1/((1+zerorate2)**w) for w in range(1,31)])

    swap1 = float1 - fix1
    swap2 = float2 - fix2

    return (swap2-swap1)/swap2*100