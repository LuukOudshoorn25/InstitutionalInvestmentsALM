# Import some of the standard packages
import pandas as pd
import numpy as np
def get_data():
    # Read in the data into seperate pd dataframes
    df_swap = pd.read_csv('./Q1_swaprates.csv',header=None)
    df_swap['maturity'] = np.arange(1,len(df_swap)+1)
    df_swap = df_swap.set_index('maturity')
    df_swap.columns = ['name','swaprate']
    df_zerocurve = pd.read_csv('./Q1_zerocurve.csv').set_index('maturity')
    df_cashflows = pd.read_csv('./Q2_cashflows.csv').set_index('maturity')

    return df_swap, df_zerocurve, df_cashflows