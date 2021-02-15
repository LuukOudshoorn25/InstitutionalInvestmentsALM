import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class vasicek():
    def __init__(self):
        """Init function for Vasicek"""
        return
    
    def iterate(self, r, lambda_):
        dW = np.random.randn(len(r))
        
        kappa=0.35
        sigma=0.5/100
        theta = -0.52
        dt = 0.01
        dW = dW  - lambda_
        dr = -kappa*(r-theta)*dt + sigma*dW*dt
        
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
        eval_func = lambda x : np.abs(self.terminal_rate(x) - 0.23)
        est = minimize(eval_func, x0=-50,method='Powell')
        return est.x[0]


    #def term_structure(self):#
