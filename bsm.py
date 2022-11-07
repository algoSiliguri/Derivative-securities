import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import norm
import numpy as np
import datetime as dt
from utilities import Utilities

class BSM:
    
    def __init__(self, days_to_expiry, strike_price, call_or_put):

        self.days_to_expiry = days_to_expiry
        self.strike_price = strike_price
        self.call_or_put = call_or_put
        self.spot_price = 0
        self.interest_rates = 0
        self.dividend = 0
        self.iv = 0
        self.cp = 0
    
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
        self.spot_price = df_SPX['Adj Close']

    ## Calculating implied volatility of a specific strike
    def calc_implied_vol(self):
        
        file_path = Utilities.getFilePath("iv")
        df = pd.read_csv(file_path)
        df_od = df.loc[df['Trade dAte'] == '12/08/2015'].copy()
        df_od.loc[:,'Strike x 1000'] = df_od['Strike x 1000'].div(1000)
        df_od = df_od.rename(columns = {"Strike x 1000": "Strike"})
        df_od = df_od.reset_index()
        del df_od['index']
        df_iv = df_od.loc[(df_od['Strike'] == self.strike_price) & (df_od['Put=1 Call=0']==self.call_or_put)]
        self.iv = df_iv['Implied Vol'].loc[df_iv["Open Interest"]==df_iv["Open Interest"].max()]

    
    ## Determine which option formula to use
    def __OptType(self):
        
        if self.call_or_put == 0:
            return 1
        else:
            return -1
    
    ## Calculating options value
    def calc_option_value(self):
        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend + 0.5 * self.iv**2) * self.days_to_expiry) / (self.iv * np.sqrt(self.days_to_expiry))
        d2 = d1 - self.iv * np.sqrt(self.days_to_expiry)
        self.call_or_put = self.__OptType()

        return self.call_or_put*(self.spot_price * np.exp(-self.dividend * self.days_to_expiry) * norm.cdf(self.call_or_put*d1) 
                                 - self.strike_price * np.exp(-self.interest_rates * self.days_to_expiry) * norm.cdf(self.call_or_put*d2))

bsm = BSM(30,2090,0)
print(bsm.calc_spotprice_SPX())
#print(bsm.calc_option_value())