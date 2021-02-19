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
        PV = self.present_day_value()
        contrib_df = pd.DataFrame({'Year':[],'Contribution':[]}).set_index('Year')
        for maturity, row in self.df.iterrows():
            pre = 100*(maturity**2 + maturity)/(1+row.zerorate/100)**2
            upper = row.cashflow / ((1+row.zerorate/100)**maturity)
            lower = PV
            modconvex += pre*upper/lower
            contrib_df.loc[maturity] = pre*upper/lower
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
    """Get modified DV01 for 30 year swap"""
    # Calculate the ModDV01 of the fixed lag 
    k = swaprate/100
    zerorate = zerorate.values.flatten()
    fixed=0
    for i in range(0,30):
        T = i+1
        disc_factor = (1+zerorate[T]/100)
        # Intermediate payments
        upper = (k/disc_factor**T) * T
        lower = 1e4 * disc_factor
        fixed += upper/lower
    # Last payment of notional
    upper = (1/disc_factor**T) * T
    lower = 1e4 * disc_factor
    fixed += upper/lower
    #Calculate ModDV01 for floating lag
    floating = ((zerorate[0]/100+1)/(1+zerorate[1]/100)) / (10000*(1+zerorate[1]/100))
    return 100*(fixed-floating)

def modDV01_bond(rate, N):
    """Get ModDV01 of the bond investment"""
    zerorate=rate/100
    k=rate/100
    T=1
    # Only one payment in one year, equal to notional (1) plus rate of the bond.
    disc_factor = (1+zerorate/100)
    upper = ((1+k)/disc_factor**T) * T
    lower = 1e4 * disc_factor
    # Multiply times notional to get DV01 of cash investment
    return N*upper/lower

def swapvalue(swaprate, zerocurve, maturity,notional):
    zerocurve = zerocurve.values.flatten()
    # Fixed leg, ie annual payments
    Vfixed = 0
    for i in range(maturity):
        # payout is one year ahead
        T = i+1
        # payment 
        discount = (1+zerocurve[i]/100)**T
        Vfixed += (swaprate/100) / discount
    # And final payment of the notional
    Vfixed += 1/(1+zerocurve[-1]/100)**maturity

    # floating leg
    Vfloat = (1+zerocurve[0]/100) / ((1+zerocurve[0]/100))
    swapvalue = Vfixed - Vfloat
    return swapvalue*notional