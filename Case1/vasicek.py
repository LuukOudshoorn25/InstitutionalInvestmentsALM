import numpy as np
import pandas as pd

class vasicek():
    def __init__(self):
        """Init function for Vasicek"""
        return
    
    def iterate(self, r):
        dW = np.random.randn(len(r))
        kappa=0.35
        sigma=0.5/100
        theta = -0.52
        dr = -kappa*(r-theta)*dt + sigma*dW
        return r+dr

    def simulate(self):
        N=1000
        

    