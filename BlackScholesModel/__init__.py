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
        self.mid_bid_ask = 0

    ## Determine which option formula to use
    def __option_type(self):

        if self.call_or_put == 0:
            return 1
        else:
            return -1

    ## A function to return d1 in BSM
    def __get_d1(self, vol=0):

        if vol == 0:
            self.calc_implied_vol()
        else:
            self.iv = vol

        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend +
              0.5 * self.iv**2) * self.years_to_expiry) / (self.iv * np.sqrt(self.years_to_expiry))
        return d1

    ## A function to return d2 in BSM
    def __get_d2(self):

        d1 = self.__get_d1()
        d2 = d1 - self.iv * np.sqrt(self.years_to_expiry)
        return d2

    ## Find the option mteric data for the given date; drop all -99.99 IV data
    def __get_om_data(self):

        df_od = ut.Utilities.get_option_metric_data()
        df_iv = df_od.loc[(df_od['Strike'] == self.strike_price) & (
            df_od['Put=1 Call=0'] == self.call_or_put)]
        df_iv = df_iv.loc[df_iv["Open Interest"]
                          == df_iv["Open Interest"].max()]
        return df_iv

    ## A function to calcultae vega
    def __calc_vega(self, vol):

        d1 = self.__get_d1(vol)
        return self.spot_price * ut.Utilities.n(d1) * np.sqrt(self.years_to_expiry)

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
        df['Date'] = pd.TimedeltaIndex(
            df['Date'], unit='d') + dt.datetime(1899, 12, 30)
        df_SPX = df.loc[df['Date'] == pd.Timestamp(2015, 8, 12)]
        self.spot_price = df_SPX.iloc[0, 5]

    ## Calculating implied volatility of a specific strike
    def calc_implied_vol(self):

        df_iv = self.__get_om_data()
        self.mid_bid_ask = np.mean(df_iv[['Bid Price', 'Ask Price']].values)
        self.iv = df_iv.iloc[0, 7]

    ## Calculating options value
    def calc_option_value(self, vol=0):

        d1 = self.__get_d1(vol)
        d2 = self.__get_d2()
        var = self.__option_type()

        return var*(self.spot_price * np.exp(-self.dividend * self.years_to_expiry) * ut.Utilities.N(var*d1)
                    - self.strike_price * np.exp(-self.interest_rates * self.years_to_expiry) * ut.Utilities.N(var*d2))

    ##  A function to find IV using Netown Raphsen algorithm
    def imp_vol_solver(self):

        # solve for implied volatility using Newton-Raphson algorithm
        df_iv = self.__get_om_data()
        niter = 1000
        tol = 1.0e-5
        v = 0.5  # initial volatility guess
        self.mid_bid_ask = np.mean(df_iv[['Bid Price', 'Ask Price']].values)
        for i in range(0, niter):
            price = self.calc_option_value(v)
            vega = self.__calc_vega(v)
            diff = self.mid_bid_ask - price
            if (abs(diff) < tol):
                return v
            v = v + diff/vega
        return v  # exit function if hasn't converged after max iterations
