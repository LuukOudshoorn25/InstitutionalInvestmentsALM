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
from liabilityhedging import LiabHedger, modDV01_swap,modDV01_bond,swapvalue,optimize_swaps
from vasicek import vasicek
# Get data
df_swap, df_zerocurve, df_cashflows = get_data()
"""
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
print(ZC.loc[[21,40,60]].round(2).to_latex(bold_rows=True))
#plot_UFR(ZC, 'UFR.pdf')

# Now obtain ultimate forward curve
BS = bootstrap(df_swap)
UFR_forward_curve = BS.UFR_forward()
print(UFR_forward_curve.loc[[1,10,30,50]].round(2).to_latex(bold_rows=True))
#plot_UFR_fc(UFR_forward_curve, 'UFR_convergence.pdf')

# Now do the ultimate forward zerocurve with convergence numbers
ZC_long_convergence = BS.UFR_zerocurve(mode='UFR_convergence')
#plot_both_ratecurves(ZC_long_convergence,ZC_long_extrapolate, 'both_longmaturity.pdf')


# Q2: Liability Hedging

#plot_cashflows(df_cashflows)
LH1 = LiabHedger(df_cashflows)
PV1 = LH1.present_day_value()
print(PV1)
assets = 1.15*PV1
print('Total assets ', np.round(1e-9*assets,4))
modDV01_assets = modDV01_bond(-0.52,assets)
print('ModDV01 of assets ', np.round(1e-6*modDV01_assets,4))

print('Present day value of liabilities',PV1)
ModDV01_1 = LH1.ModDV01()[1]
print('Modified DV01 (in millions): ',np.round(1e-6*ModDV01_1,2))
#print('Contributions to ModDV01 (in millions): ',np.round(1e-6*LH1.ModDV01()[0].loc[[10,20,30]],2))
ModDur1_1 = LH1.modDur()[1]
print('Modified Duration (in years): ',np.round(ModDur1_1,2))
#print('Contributions to ModDur (in years): ',LH1.modDur()[0].loc[[10,20,30]])
ModConv1 = LH1.ModConv()[1]
print('Modified x Convexity (in million euros): ',np.round(ModConv1,2))
#print('Contributions to ModConv (in years): ',LH1.ModConv()[0].loc[[10,20,30]])

# Plot all zerocurves for this question in one plot
#plot_Q2_zerocurves(df_cashflows['zerorate'], df_cashflows['zerorate']-0.5, df_cashflows['zerorate']+df_cashflows['deltazerorate'],
#                   'Unshocked zero rates', 'Shock 1', 'Shock 2')

# Now add a shock of 0.5% to the zerocurve
df_cashflows['zerorate'] = df_cashflows['zerorate'] -0.5
LH2 = LiabHedger(df_cashflows)
PV2 = LH2.present_day_value()

print('Liabilities went from ', np.round(1e-9*PV1, 2), ' billion to ',np.round(1e-9*PV2, 2), 'billion')
print('Liabilities increased by ',np.round(1e-9*PV2-1e-9*PV1, 2), ' billion')

print('Modified DV01 contribution is ', np.round(1e-6*ModDV01_1*50, 2), ' million')
print('Modified convexity contribution is ', np.round(1e-6*ModConv1*50**2, 2), ' million')
print('Total contribution of DV01 and Convexity is ',np.round(1e-9*ModDV01_1*50+1e-9*ModConv1*50**2, 2), ' billion')

# Q2c: Get DV01 for 30yr swap contract
df_swap, df_zerocurve, df_cashflows = get_data()
swap30 = 0.3756
swap_DV01 = modDV01_swap(swap30,  df_cashflows['zerorate'])
print('DV01 of swap contract: ',np.round(swap_DV01,4), ' %')

# Q2c: get amount of DV01 needed
#to_hedge = 1.15*(PV1 - PV2) + 50*modDV01_assets
to_hedge = 1.15*(45.86e6) - modDV01_assets
DV01_needed = np.abs((to_hedge)/(0.002726))
print('We need (billion)', np.round(DV01_needed*1e-9,3))

#Q2d
# Refresh data
df_swap, df_zerocurve, df_cashflows = get_data()
# set shock
df_cashflows['zerorate'] = df_cashflows['zerorate'] + df_cashflows['deltazerorate']

LH3 = LiabHedger(df_cashflows)
print('Present value of liabilities is ',LH3.present_day_value())
# Get value of the swap
swapval = swapvalue(0.3756, df_cashflows['zerorate'], 30, DV01_needed)
print('Value of swap changed to ', np.round(1e-6*swapval,3), ' million')
newassets = assets + swapval
print('New total assets ',newassets)
print('New FR ',100*newassets/LH3.present_day_value())

# Q2e minimizer
effectiveness_df = pd.DataFrame({'Matchtype':[],'Portfolio':[],'New FR':[]})
df_swap, df_zerocurve, df_cashflows = get_data()
# Optimize notionals for constant FR
possible_swaps = [[10,30,40],[10,30,50],[20, 30, 40],[20, 30, 50],[30, 40, 50],[10, 20, 30],[30]]
notionals_df = pd.DataFrame({'index':[]}).set_index('index')
for i,s in enumerate(possible_swaps):
    OS = optimize_swaps(df_cashflows,s)
    OS.make_swap_curve()
    notionals,objective = OS.optimize_FR()
    print(s,notionals,objective)
    if not s==[30]:
        notionals_df.loc[i,s] = notionals
    else:
        notionals_df.loc[i,s] = notionals[0]
notionals_df = notionals_df.round(2)
notionals_df = notionals_df[[10,20,30,40,50]]
notionals_df.index = np.arange(1,8,dtype=int)
print(notionals_df.fillna('-').to_latex(bold_rows=True))

# Test performance
for portfolio,row in notionals_df.iterrows():
    r=row.dropna()
    newFR=1
    maturities = r.index
    notionals  = r.values
    OS = optimize_swaps(df_cashflows,maturities,shock='shock2')
    OS.make_swap_curve()
    newFR = OS.propagate_FR(notionals)
    effectiveness_df.loc[portfolio]=['FR',portfolio,newFR]



df_swap, df_zerocurve, df_cashflows = get_data()
# Optimize notionals for equal DV01
possible_swaps = [[10,30,40],[10,30,50],[20, 30, 40],[20, 30, 50],[30, 40, 50],[10, 20, 30],[30]]
notionals_df = pd.DataFrame({'index':[]}).set_index('index')
for i,s in enumerate(possible_swaps):
    OS = optimize_swaps(df_cashflows,s)
    OS.make_swap_curve()
    notionals, objective = OS.optimize_DV01()
    print(s,notionals,objective)
    if not s==[30]:
        notionals_df.loc[i,s] = notionals
    else:
        notionals_df.loc[i,s] = notionals[0]
notionals_df = notionals_df.round(2)
notionals_df = notionals_df[[10,20,30,40,50]]
notionals_df.index = np.arange(1,8,dtype=int)
print(notionals_df.fillna('-').to_latex(bold_rows=True))



for portfolio,row in notionals_df.iterrows():
    r=row.dropna()
    newFR=1
    maturities = r.index
    notionals  = r.values
    OS = optimize_swaps(df_cashflows,maturities,shock='shock2')
    OS.make_swap_curve()
    newFR = OS.propagate_FR(notionals)
    effectiveness_df.loc[portfolio+7]=['DV01',portfolio,newFR]

effectiveness_df = effectiveness_df.set_index(['Matchtype','Portfolio'])
effectiveness_df = effectiveness_df.unstack().T.round(2)
print(effectiveness_df.fillna('-').to_latex(bold_rows=True))
    
"""


# # Q4: Vasicek-model
VS = vasicek()
#lambda_ = VS.find_lambda()
#print(lambda_)
VS.lambda_ = -0.53
# Complete term structure of nominal interest rates
zerorates_Q = VS.termstructure_Q()
plot_vasicek_termstructure(np.arange(0,61,1), zerorates_Q, df_cashflows['zerorate'])
# calculate new nominal liabilities and obtain new swap rate
PV = VS.value_liabilities(zerorates_Q)
print('Present value of liabilities in billions under Vasicek ',np.round(PV*1e-9,3))
# Q4c: Resulting distribution after one year
final_rates = VS.one_year()
plot_oneyear_hist(100*final_rates)
# Q4d: Show all_termstructures
all_termstructures = VS.all_termstructures(distribution_r=final_rates)
plt.plot(all_termstructures.transpose())
plt.show()
# Q4d: calculate the
tracking_error = VS.valuation(cash=PV, termstructures=all_termstructures)
print('Mean difference between assets and liabilities is ', np.round(np.mean(tracking_error)))
print('Tracking error is ', np.round(np.std(tracking_error)))



# Q4b: Apply zerorates to liabilities from Q2
#_,_, df_cashflows = get_data()
#df_cashflows['zerorate'] = zerorates*100
#LH = LiabHedger(df_cashflows)
#PV = LH.present_day_value()
#print('Present value of liabilities in billions under Vasicek ',np.round(PV*1e-9,3))
#plot_zerorates(df_cashflows, fname='Vasicek_termstructure.pdf')


VS.matching()