import pandas as pd
from scipy.interpolate import interp1d
import numpy as np
import datetime as dt
import Utilities as ut

class BSM:

    def __init__(self, days_to_expiry, strike_price, call_or_put):

        self.days_to_expiry = days_to_expiry
        self.strike_price = strike_price
        self.call_or_put = call_or_put
        self.years_to_expiry = days_to_expiry/365
        self.spot_price = 0
        self.interest_rates = 0
        self.dividend = 0
        self.iv = 0

    ## Calculating ineterest rates from zero curve using linear interpolation
    def calc_interest_rates(self):

        file_path = ut.Utilities.getFilePath("interest_rates")
        df = pd.read_csv(file_path)
        df_data = df.loc[df['Date'] == '12/08/2015']
        X = df_data['Days']
        Y = df_data['Rate']

        interpolate_x = self.days_to_expiry
        y_interp = interp1d(X, Y)
        self.interest_rates = y_interp(interpolate_x)/100

    ## Calculating the dividend yield
    def calc_dividend(self):

        file_path = ut.Utilities.getFilePath("dividend")
        df = pd.read_csv(file_path)
        df_Div = df.loc[df['Date'] == '12/08/2015']
        self.dividend = df_Div.values[0, 2]/100

    ## Calculating spot price of SPX on '12/08/2015'
    def calc_spotprice_SPX(self):

        file_path = ut.Utilities.getFilePath("SPX")
        df = pd.read_csv(file_path)
        df['Date'] = pd.TimedeltaIndex(df['Date'], unit='d') + dt.datetime(1899,12,30)
        df_SPX = df.loc[df['Date'] == pd.Timestamp(2015,8,12)]
        self.spot_price = df_SPX.iloc[0,5]

    ## Calculating implied volatility of a specific strike
    def calc_implied_vol(self):

        file_path = ut.Utilities.getFilePath("iv")
        df = pd.read_csv(file_path)
        df_od = df.loc[df['Trade dAte'] == '12/08/2015']
        df_iv = df_od.loc[(df_od['Strike x 1000'] == self.strike_price*1000) & (df_od['Put=1 Call=0']==self.call_or_put)]
        df_iv = df_iv.loc[df_iv["Open Interest"] == df_iv["Open Interest"].max()]
        self.iv = df_iv.iloc[0][7]

    ## Determine which option formula to use
    def __option_type(self):

        if self.call_or_put == 0:
            return 1
        else:
            return -1

    ## Calculating options value
    def calc_option_value(self):

        self.calc_dividend()
        self.calc_interest_rates()
        self.calc_implied_vol()
        self.calc_spotprice_SPX()

        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend + 0.5 * self.iv**2) * self.years_to_expiry) / (self.iv * np.sqrt(self.years_to_expiry))
        d2 = d1 - self.iv * np.sqrt(self.years_to_expiry)
        var = self.__option_type()
        
        #print(self.strike_price, self.spot_price, self.interest_rates, self.dividend, self.iv, self.days_to_expiry, self.call_or_put)

        #print(d1, d2)

        return var*(self.spot_price * np.exp(-self.dividend * self.years_to_expiry) * ut.Utilities.N(var*d1) 
                                  - self.strike_price * np.exp(-self.interest_rates * self.years_to_expiry) * ut.Utilities.N(var*d2))

    def imp_vol_option_value(self,v):
        
        self.calc_dividend()
        self.calc_interest_rates()
        self.calc_spotprice_SPX()
        
        #print(self.strike_price, self.spot_price, self.interest_rates, self.dividend, self.iv, self.days_to_expiry, self.call_or_put)
        
        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend + 0.5 * v**2) * self.years_to_expiry) / (v * np.sqrt(self.years_to_expiry))
        d2 = d1 - v * np.sqrt(self.years_to_expiry)
        var = self.__option_type()
        
        #print(d1, d2)

        return var*(self.spot_price * np.exp(-self.dividend * self.years_to_expiry) * ut.Utilities.N(var*d1) 
                                  - self.strike_price * np.exp(-self.interest_rates * self.years_to_expiry) * ut.Utilities.N(var*d2))
    
    def calc_vega(self,v):
        
        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend + 0.5 * v**2) * self.years_to_expiry) / (v * np.sqrt(self.years_to_expiry))
        return self.spot_price * ut.Utilities.n(d1) * np.sqrt(self.years_to_expiry)
    
    def imp_vol_solver(self):
        
        # solve for implied volatility using Newton-Raphson algorithm
        file_path = ut.Utilities.getFilePath("iv")
        df = pd.read_csv(file_path)
        df_od = df.loc[df['Trade dAte'] == '12/08/2015']
        df_iv = df_od.loc[(df_od['Strike x 1000'] == self.strike_price*1000) & (df_od['Put=1 Call=0']==self.call_or_put)]
        
        niter = 1000
        tol = 1.0e-5
        v = 0.5 # initial volatility guess
        self.mid_bid_ask = np.mean(df_iv[['Bid Price', 'Ask Price']].loc[df_iv["Volume"]==df_iv["Volume"].max()].values)
        for i in range(0, niter):
            price = self.imp_vol_option_value(v)
            vega = self.calc_vega(v)
            diff = self.mid_bid_ask - price
            if (abs(diff) < tol):
                #print(i) # Check on how fast function converges
                return v
            v = v + diff/vega
        return v # exit function if hasn't converged after max iterations