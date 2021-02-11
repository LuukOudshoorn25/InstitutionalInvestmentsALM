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
from zerocurve import bootstrap
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
ZC = BS.UFR()
print(ZC.loc[[21,40,60]])
#plot_URF(ZC)