import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from joblib import Parallel, delayed
from liabilityhedging import LiabHedger, modDV01_swap,modDV01_bond,swapvalue
from datalib import get_data

class vasicek():
    def __init__(self):
        """Init function for Vasicek"""
        self.kappa=0.35
        self.sigma=0.5/100
        self.theta = -0.52/100
        self.dt = 0.01
        self.r0 = -0.52/100
        return
    
    def iterate(self, r, lambda_):
        dW = np.random.randn(len(r))
        dW = dW  - lambda_
        dr = -self.kappa*(r-self.theta)*self.dt + self.sigma*dW*self.dt
        return r+dr

    def simulate(self, lambda_):
        N=1000
        datas = np.zeros((1000,1000))
        for i in range(datas.shape[-1]-1):
            datas[:,i+1] = self.iterate(datas[:,i],lambda_)
        return datas
    
    def terminal_rate(self, lambda_):
        datas = self.simulate(lambda_[0])
        return np.median(np.median(datas, axis=0)[-100:])
        
    def find_lambda(self):
        eval_func = lambda x : np.abs(self.terminal_rate(x) - 0.0023)
        est = minimize(eval_func, x0=-50,method='Powell')
        self.lambda_ = est.x[0]
        return est.x[0]

    def stochastic_integral(self,T,Npaths=10000):
        t = np.linspace(0,T,200)
        N = len(t)
        x = np.zeros((N,Npaths))
        for i in range(N-1):
            dt = t[i+1]-t[i]
            dWt = np.random.normal(0,dt,size=(Npaths))
            x[i+1] = x[i] + np.exp(self.kappa*t[i])*dWt
        return np.median(x[-1,:])

    def bondprice(self,t):
        thetatilde = self.theta - self.sigma*self.lambda_ / self.kappa
        r = (self.r0 - thetatilde)*np.exp(-self.kappa*t)+thetatilde + self.sigma*np.exp(-self.kappa*t)*self.stochastic_integral(t)
        return r
    
    def termstructure(self):
        maturities = np.arange(0,61,1)
        return np.array([self.bondprice(T) for T in maturities])
    
    def worker(self,i):
        t=1
        thetatilde = self.theta - self.sigma*self.lambda_ / self.kappa
        return (self.r0 - thetatilde)*np.exp(-self.kappa*t)+thetatilde + self.sigma*np.exp(-self.kappa*t)*self.stochastic_integral(t,1)

    def one_year(self):
        N=int(1e4)
        final_rates = Parallel(n_jobs=22)(delayed(self.worker)(i) for i in range(N))
        final_rates = np.array(final_rates)
        return final_rates

    def SWAP_notional(self):
        df_swap, df_zerocurve, df_cashflows = get_data()
        LH1 = LiabHedger(df_cashflows)
        PV1 = LH1.present_day_value()
        assets = 1.15*PV1
        df_cashflows['zerorate'] = df_cashflows['zerorate'] -0.5
        LH2 = LiabHedger(df_cashflows)
        PV2 = LH2.present_day_value()
        modDV01_assets = modDV01_bond(-0.52,assets)
        to_hedge = PV1 - PV2 + 50*modDV01_assets
        swapnotional = np.abs((to_hedge/50)/(0.002726))
        return swapnotional



    def matching(self):
        # Obtain interest rates from Vasicek model for one year (scenario approach)
        oneyear_rates = self.one_year()
        # Get swap notional
        notional = self.SWAP_notional()
        swapval = swapvalue(0.3756, pd.Series(oneyear_rates), 30, notional)