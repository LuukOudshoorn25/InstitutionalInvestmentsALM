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
 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
plt.style.use('../MNRAS_stylesheet')
def plot_swaprates(df_swap):
    plt.plot(df_swap.index, df_swap.swaprate,color='black',lw=1)
    plt.xlabel('Maturity [years]')
    plt.ylabel('Swap rate [%]')
    plt.tight_layout()
    plt.show()

def plot_UFR(ZC,fname=None):
    xnew = np.arange(1,len(ZC),0.01)
    f1 = interp1d(ZC.index, ZC['Zero rate'], kind='quadratic')
    plt.plot(xnew, f1(xnew), lw=1,color='black')
    plt.scatter(ZC.index, ZC['Zero rate'],color='dodgerblue',s=3)
    plt.xlabel('Maturity [years]')
    plt.ylabel('Zerorate [%]')
    plt.tight_layout()
    if fname:
        plt.savefig(fname)
    plt.show()

def plot_UFR_fc(df,fname=None):
    xnew = np.arange(1,len(df),0.01)
    f1 = interp1d(df.index, df['URF_forward'], kind='quadratic')
    plt.plot(xnew, f1(xnew), lw=1,color='black')
    plt.scatter(df.index, df['URF_forward'],color='dodgerblue',s=3)
    plt.xlabel('Maturity [years]')
    plt.ylabel('UFR forward rate [%]')
    plt.tight_layout()
    if fname:
        plt.savefig(fname)
    plt.show()

def plot_zcs(df_swap,ZC, df_zerocurve,fname=None):
    # Obtain difference between swap and zero rate to enhance plotting
    diff = pd.merge(df_swap,ZC,left_index=True,right_index=True)
    diff['diff'] = 100*(diff['Zero rate'] - diff['swaprate'])

    xnew = np.arange(1,20,0.01)

    fig, (a0, a1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]},figsize=(6,4),sharex=True)
    #a0.plot(df_swap.index, df_swap.swaprate,color='black',lw=1, ls='--', label='Swap rates')
    a0.scatter(df_zerocurve.index, df_zerocurve, s=5,color='dodgerblue',label='Mark-Jan zerocurve')
    # Do some spline interpolation
    f1 = interp1d(df_swap.index, df_swap.swaprate, kind='quadratic')
    a0.plot(xnew, f1(xnew),color='black',lw=1, ls='--', label='Swap rates')
    
    f2 = interp1d(ZC.index, ZC['Zero rate'], kind='quadratic')
    #a0.plot(ZC.index, ZC['Zero rate'],color='black',lw=1, label='Zero rate')
    a0.plot(xnew, f2(xnew),color='black',lw=1, label='Zero rate')
    
    f3 = interp1d(diff.index, diff['diff'], kind='quadratic')
    #a1.plot(diff.index, diff['diff'],color='black',lw=1, label='Zero rate - swap rate')
    a1.plot(xnew, f3(xnew),color='black',lw=1, label='Zero rate - swap rate')
    
    for ax in [a0,a1]:
        ax.axhline(0,ls='--',lw=0.5,color='black')
        ax.set_xlim(1,20)
        ax.legend(frameon=1)
    
    a0.set_ylabel('Rate (%)')
    a1.set_ylabel(r'$\Delta\,r$ (bp)')
    a1.set_xlabel('Time [yr]')
    plt.tight_layout(pad=-0.5)
    if fname:
        plt.savefig(fname,bbox_inches='tight')
    plt.show()


def plot_both_ratecurves(ZC_long_convergence, ZC_long_extrapolate):
    plt.plot(ZC_long_convergence,label='convergence')
    plt.plot(ZC_long_extrapolate, label='extrapolate')
    plt.xlabel('Maturity [years]')
    plt.ylabel('UFR forward rate [%]')
    plt.legend(frameon=1)
    plt.show()