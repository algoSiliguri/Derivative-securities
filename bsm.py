## Class to to initialise inputs to a Black Scholes Model

import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import norm
import numpy as np
import datetime as dt
from utilities import Utilities

class BSM:
    ## Non class variables
    configs = Utilities.read_properties()

    def __init__(self, days_to_expiry, strike_price):

        self.days_to_expiry = days_to_expiry
        self.strike_price = strike_price
        self.spot_price = 0
        self.interest_rates = 0
        self.dividend = 0
        self.iv = 0
    
    ## Calculating ineterest rates from zero curve using linear interpolation
    def calc_interest_rates(self):

        file_path = Utilities.getFilePath("interest_rates")
        df = pd.read_csv(file_path)
        df_data = df.loc[df['Date'] == '12/08/2015']
        X = df_data['Days']
        Y = df_data['Rate']

        interpolate_x = self.days_to_expiry
        self.days_to_expiry = self.days_to_expiry / 365
        y_interp = interp1d(X,Y)
        self.interest_rates = y_interp(interpolate_x)/100

    ## Calculating the dividend yield
    def calc_dividend(self):

        file_path = Utilities.getFilePath("dividend")
        df = pd.read_csv(file_path)
        df_Div = df.loc[df['Date'] == '12/08/2015']
        self.dividend = df_Div.values[0,2]/100

    ## Calculating spot price of SPX on '12/08/2015'
    def calc_spotprice_SPX(self):

        file_path = Utilities.getFilePath("SPX")
        df = pd.read_csv(file_path)
        df['Date'] = pd.TimedeltaIndex(df['Date'], unit='d') + dt.datetime(1899,12,30)
        df_SPX = df.loc[df['Date'] == pd.Timestamp(2015,8,12)]
        self.spot_price = df_SPX.values[0,4]

    ## Calculating implied volatility of a specific strike
    def calc_implived_vol(self):
        pass

    ## Calculating call options value
    def CallOptionValue(self):

        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend + 0.5 * self.iv**2) * self.days_to_expiry) / (self.iv * np.sqrt(self.days_to_expiry))
        d2 = d1 - self.iv * np.sqrt(self.days_to_expiry)

        return self.spot_price * np.exp(-self.dividend * self.days_to_expiry) * norm.cdf(d1) - self.strike_price * np.exp(-self.interest_rates * self.days_to_expiry) * norm.cdf(d2)




                            #####    Delete this part of code once done ###########

# ## Import option data
# file_path = os.getcwd() + "/project/OptionData.csv"
# df = pd.read_csv(file_path)
# df_od = df.loc[(df['Trade dAte'] == '12/08/2015') & (df['Put=1 Call=0'] == 0)].copy()
# df_od.loc[:,'Strike x 1000'] = df_od['Strike x 1000'].div(1000)
# df_od = df_od.rename(columns = {"Strike x 1000": "Strike"})
# df_od = df_od.reset_index()
# del df_od['index']

# ## Get SPX spot price
# file_path = os.getcwd() + "/project/SPXDaily1950.csv"
# df = pd.read_csv(file_path)
# df['Date'] = pd.TimedeltaIndex(df['Date'], unit='d') + dt.datetime(1899,12,30)
# df_SPX = df.loc[df['Date'] == pd.Timestamp(2015,8,12)]

# file_path = os.getcwd() + "/project/SPXDivYield.csv"
# df = pd.read_csv(file_path)
# df_Div = df.loc[df['Date'] == '12/08/2015']

# ## Define input parameters
# SPX_close = df_SPX.values[0,4]
# # Two options with same strike closest to on the money; Choose option with higher trading volume
# ind = df_od[abs(df_od['Strike']-SPX_close)==min(abs(df_od['Strike']-SPX_close))].sort_values(by=['Volume'], ascending=False).index[0]

# S	= SPX_close
# K	= df_od.values[ind,3]
# r	= bsm.interest_rates/100
# T	= DaysToExpiry/365
# sigma	= df_od.values[ind,7]
# q = df_Div.values[0,2]/100

# ## Main Function
# print('Calculated Option Price based on Implied Volatility:\n',
#        BSM.CallOptionValue(S, K, r, sigma, T, q))