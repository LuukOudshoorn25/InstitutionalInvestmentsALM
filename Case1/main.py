###############################################
###                                         ###
###     Main file for the Instit Invest.    ###
###        and ALM Case 1 assignment        ###
###               Luuk Oudshoorn            ###
###            Willem-Jan de Voogd          ###
###                Mees Tierolf             ###
###      All quantitative  (Fin. Econ)      ###
###                                         ###
###############################################

# Import some of the standard packages
import pandas as pd
import numpy as np

# Import functios from other files
from datalib import get_data
from plottinglib import *
from termstructure import bootstrap
from liabilityhedging import LiabHedger

# Get data
df_swap, df_zerocurve, df_cashflows = get_data()

# Q1: Term structure of interest rates
# Let us first plot the swap rates as function of maturity
#plot_swaprates(df_swap)

# Time to bootstrap the zerocurve. Given are swap rates for different maturities. 
# All swaps are fixed versus floating. The floating lag is always the one year swap
BS = bootstrap(df_swap)
ZC = BS.get_zerocurve()
# Merge with values from Mark-Jan to check if we indeed are OK
merged = BS.merge(df_zerocurve)

# Plot the obtained zerocurve together with Mark-Jan's zero curve and the swapcurve
#plot_zcs(df_swap,ZC, df_zerocurve,fname='zerocurve.pdf')

# Calculate the forward rate from 19 to 20 years
f19_20 = BS.forward_rate()
print('Forward rate from 19 to 20 years (in %): ',np.round(f19_20,3))

# Now do the ultimate forward zerocurve projection
ZC_long_extrapolate = BS.UFR_zerocurve()
print(ZC.loc[[21,40,60]])
#plot_UFR(ZC)

# Now obtain ultimate forward curve
BS = bootstrap(df_swap)
UFR_forward_curve = BS.UFR_forward()
print(UFR_forward_curve.loc[[1,10,30,50]])
#plot_UFR_fc(UFR_forward_curve)

# Now do the ultimate forward zerocurve with convergence numbers
ZC_long_convergence = BS.UFR_zerocurve(mode='UFR_convergence')
#plot_both_ratecurves(ZC_long_convergence,ZC_long_extrapolate)


# Q2: Liability Hedging
LH1 = LiabHedger(df_cashflows)
PV1 = LH1.present_day_value()
print('Present day value of liabilities',PV1)
ModDV01_1 = LH1.ModDV01()[1]
print('Modified DV01 (in millions): ',np.round(1e-6*ModDV01_1,2))
print('Contributions to ModDV01 (in millions): ',np.round(1e-6*LH1.ModDV01()[0].loc[[10,20,30]],2))
ModDur1_1 = LH1.modDur()[1]
print('Modified Duration (in years): ',np.round(ModDur1_1,2))
print('Contributions to ModDur (in years): ',LH1.modDur()[0].loc[[10,20,30]])

# Now add a shock of 0.5% to the zerocurve
df_cashflows['zerorate'] = df_cashflows['zerorate'] -0.5
LH2 = LiabHedger(df_cashflows)
PV2 = LH2.present_day_value()
print('Present day value of liabilities',LH2.present_day_value())
ModDV01_2 = LH2.ModDV01()[1]
print('Modified DV01 (in millions): ',np.round(1e-6*ModDV01_2,2))
print('Contributions to ModDV01 (in millions): ',np.round(1e-6*LH2.ModDV01()[0].loc[[10,20,30]],2))
ModDur2 = LH2.modDur()[1]
print('Modified Duration (in years): ',np.round(ModDur2,2))
print('Contributions to ModDur (in years): ',LH2.modDur()[0].loc[[10,20,30]])


print('Liabilities went from ', np.round(1e-9*PV1, 2), ' billion to ',np.round(1e-9*PV2, 2), 'billion')
print('Modified DV01 went from ', np.round(1e-6*ModDV01_1, 2), ' million to ',np.round(1e-6*ModDV01_2, 2), 'million')