## Class to to initialise inputs to a Black Scholes Model

import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import norm
from utilities import Utilities
import math as m
import datetime as dt
import os

class BSM:

    def __init__(self, days_to_expiry):

        self.days_to_expiry = days_to_expiry
        self.interest_rates = 0
        self.dividend = 0
        self.iv = 0
    
    ## Calculating ineterest rates from zero curve using linear interpolation
    def calc_interest_rates(self):

        file_path = Utilities.getCurrDir() + "/project/ZeroCurve.csv"
        df = pd.read_csv(file_path)
        df_data = df.loc[df['Date'] == '12/08/2015']
        X = df_data['Days']
        Y = df_data['Rate']

        interpolate_x = self.days_to_expiry
        y_interp = interp1d(X,Y)
        self.interest_rates = y_interp(interpolate_x)
        
    def CallOptionValue(S, K, r, sigma, T, q):
        d1 = (m.log(S/K) + (r -q + 0.5 * sigma**2) * T)/(sigma * m.sqrt(T))
        d2 = d1 - sigma * m.sqrt(T)
        return S *m.exp(-q*T) * norm.cdf(d1) - K * m.exp(-r*T) * norm.cdf(d2)     


bsm = BSM(int(input("Days to expiry: ")))
bsm.calc_interest_rates()
#print(bsm.interest_rates)

## Import option data
file_path = os.getcwd() + "/project/OptionData.csv"
df = pd.read_csv(file_path)
df_od = df.loc[(df['Trade dAte'] == '12/08/2015') & (df['Put=1 Call=0'] == 0)].copy()

df_od.loc[:,'Strike x 1000'] = df_od['Strike x 1000'].div(1000)
df_od = df_od.rename(columns = {"Strike x 1000": "Strike"})

df_od = df_od.reset_index()
del df_od['index']

file_path = os.getcwd() + "/project/SPXDaily1950.csv"
df = pd.read_csv(file_path)
df['Date'] = pd.TimedeltaIndex(df['Date'], unit='d') + dt.datetime(1899,12,30)
df_SPX = df.loc[df['Date'] == pd.Timestamp(2015,8,12)]

file_path = os.getcwd() + "/project/SPXDivYield.csv"
df = pd.read_csv(file_path)
df_Div = df.loc[df['Date'] == '12/08/2015']

## Define input parameters
SPX_close = df_SPX.values[0,4]
# Two options with same strike closest to on the money; Choose option with higher trading volume
ind = df_od[abs(df_od['Strike']-SPX_close)==min(abs(df_od['Strike']-SPX_close))].sort_values(by=['Volume'], ascending=False).index[0]

S	= SPX_close
K	= df_od.values[ind,3]
r	= bsm.interest_rates/100
T	= 30/365
sigma	= df_od.values[ind,7]
q = df_Div.values[0,2]/100

## Main Function
print('Calculated Option Price based on Implied Volatility:\n',
       BSM.CallOptionValue(S, K, r, sigma, T, q))