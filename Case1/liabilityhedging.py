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
from scipy.optimize import minimize

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
    for i in range(1,maturity+1):
        # payout is one year ahead
        # payment
        discount = (1+zerocurve[i]/100)**i
        Vfixed += (swaprate/100) / discount
    # And final payment of the notional
    Vfixed += 1/((1+zerocurve[maturity]/100)**maturity)
    # floating leg
    Vfloat = (1+zerocurve[0]/100) / ((1+zerocurve[0]/100))
    swap = Vfixed - Vfloat
    return swap*notional

def bondvalue(bondrate, zerocurve, maturity, notional):
    zerocurve = zerocurve.values.flatten()
    # Fixed leg, ie annual payments
    Vfixed = 0
    for i in range(1,maturity+1):
        # payout is one year ahead
        # payment
        discount = (1+zerocurve[i]/100)**i
        Vfixed += (bondrate/100) / discount
    # And final payment of the notional
    Vfixed += 1/((1+zerocurve[maturity]/100)**maturity)
    return Vfixed

class optimize_swaps():
    def __init__(self,df, maturities):
        self.df = df
        self.maturities = maturities
        self.DV01_bond()
    
    def minimize_func(self,T):
        # Calculate swaprate
        # Minimize absolute value of the swap given the swaprate
        function = lambda x: np.abs(swapvalue(x,self.df.zerorate, T, 100))
        # For each time, find the swap rate by minimizing the absolute value
        res = minimize(function, x0 = 0.3)
        swaprate = res.x
        return swaprate
    
    def make_swap_curve(self):
        # Create time axis
        times = np.arange(1,51)
        # Create empty df to fill
        swappers = pd.DataFrame({'Maturity':times, 'Rate':times}).set_index('Maturity')
        for T in times:
            # Get the swaprate
            swappers.loc[T] = self.minimize_func(T)
        self.swappers = swappers
        return swappers

    def DV01_liabilities(self):
        # Get DV01 of the liabilities using the original zerocurve
        LH = LiabHedger(self.df)
        PV1 = LH.present_day_value()
        # Change zerocurve by one bp
        shocked = self.df.copy()
        shocked['zerorate'] = shocked['zerorate']+0.01
        LH = LiabHedger(shocked)
        PV2 = LH.present_day_value()
        DV01_liabilities = PV1 - PV2
        return PV1,PV2,DV01_liabilities

    def DV01_bond(self):
        # The asssets have some interest rate sensitivity
        self.assets = 1.15*self.DV01_liabilities()[0]
        moddv01 = modDV01_bond(-0.52,self.assets)
        return moddv01

    def DV01_swaps(self):
        maturities = self.maturities
        # Get corresponding swaprates
        swaprates = self.swappers.loc[maturities]
        # Get modified DV01 for the swaps modDV01_swap
        modDV01_swaps = [modDV01_swap(w, self.df.zerorate) for w in swaprates.values.flatten()]
        return np.array(modDV01_swaps)

    def values_swaps(self,zerocurve, notionals):
        maturities = self.maturities
        # Get corresponding swaprates
        swaprates = self.swappers.loc[maturities]
        # Get value of the swap given the new zerocurve
        
        newvalues = [swapvalue(swaprates.loc[maturities[w]], zerocurve, maturities[w],notionals[w]) for w in range(len(maturities))]
        return np.sum(newvalues)

    def propagate_FR(self,notionals):
        # apply zerocurve shift
        shocked = self.df.copy()
        notionals = np.array(notionals)*1e9
        shocked['zerorate'] = shocked['zerorate'] - 0.01#shocked['deltazerorate']
        # Get new liabilities
        LH = LiabHedger(shocked)
        PV = LH.present_day_value()
        # Get new assets
        swapval = self.values_swaps(shocked['zerorate'], notionals)
        bondval = bondvalue(-0.52,shocked['zerorate'],1,self.assets)
        newassets = self.assets + swapval + bondval
        newFR = newassets / PV
        return newFR*100

    def propagate_DV01(self,notionals):
        # apply zerocurve shift
        shocked = self.df.copy()
        notionals = np.array(notionals)*1e9
        # Get DV01 of liabilities
        #PV1,PV2,DV01_liabilities = self.DV01_liabilities()
        DV01_liabilities = 45.86e6
        #print('DV01 liabilities',DV01_liabilities)
        # Get DV01 of assets
        DV01_assets = self.DV01_bond()
        #print('DV01 swaps ',self.DV01_swaps())
        DV01_assets += np.sum(notionals*self.DV01_swaps()/100)
        # Get difference between DV01
        return np.abs(1.15*DV01_liabilities - DV01_assets)
        

    def optimize_FR(self):
        # Maturities are fixed to those in def DV01_swaps
        # Notionals can be optimized
        # We consider the zerocurve change from column D
        function = lambda x: np.abs(self.propagate_FR(x)-115)
        res = minimize(function, x0=[10,10,10],method='SLSQP')
        return res.x, res.fun

    def optimize_DV01(self):
        # Maturities are fixed to those in def DV01_swaps
        # Notionals can be optimized
        # We consider the zerocurve change from column D
        bounds = len(self.maturities)*[(0,np.inf)]
        res = minimize(self.propagate_DV01, x0=len(self.maturities)*[2],method='SLSQP',bounds=bounds)
        return res.x, res.fun

