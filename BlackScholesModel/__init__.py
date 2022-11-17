import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
import numpy as np
import Utilities as ut
import datetime as dt


class BSM:
    check_iv = False
    bsm_option_price = 0
    days_to_expiry = 0

    def __init__(self, days_to_expiry, strike_price, call_or_put):

        self.days_to_expiry = days_to_expiry
        self.strike_price = strike_price
        self.call_or_put = call_or_put
        self.spot_price = 0
        self.interest_rates = 0
        self.dividend = 0
        self.iv = 0
        self.brent_iv = 0.01
        self.mid_bid_ask = 0

    ## Determine which option formula to use
    def __option_type(self):

        if self.call_or_put == 0:
            return 1
        else:
            return -1

    ## A function to return d1 in BSM
    def __get_d1(self):

        if BSM.check_iv:
            iv = self.brent_iv
        else:
            iv = self.iv

        d1 = (np.log(self.spot_price/self.strike_price) + (self.interest_rates - self.dividend +
              0.5 * iv**2) * self.days_to_expiry/365) / (iv * np.sqrt(self.days_to_expiry/365))
        return d1

    ## A function to return d2 in BSM
    def __get_d2(self):

        if BSM.check_iv:
            iv = self.brent_iv
        else:
            iv = self.iv

        d1 = self.__get_d1()
        d2 = d1 - iv * np.sqrt(self.days_to_expiry/365)
        return d2

    ## Find the option mteric data for the given date; drop all -99.99 IV data
    def __get_om_data(self):

        df_od = ut.Utilities.get_option_metric_data()
        df_iv = df_od.loc[(df_od['Strike'] == self.strike_price) & (
            df_od['Put=1 Call=0'] == self.call_or_put)]
        df_iv = df_iv.loc[df_iv["Open Interest"]
                          == df_iv["Open Interest"].max()]
        return df_iv

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
    def calc_option_value(self):

        d1 = self.__get_d1()
        d2 = self.__get_d2()
        var = self.__option_type()

        option_price = var*(self.spot_price * np.exp(-self.dividend * self.days_to_expiry/365) * ut.Utilities.N(var*d1)
                            - self.strike_price * np.exp(-self.interest_rates * self.days_to_expiry/365) * ut.Utilities.N(var*d2))

        if not BSM.check_iv:
            BSM.bsm_option_price = option_price

        return option_price

    ##  A function to find IV using Brent's algorithm
    def imp_vol_solver(self):

        def option_obj(vol):
            self.brent_iv = vol
            return abs(self.calc_option_value() - self.mid_bid_ask)

        minimize_scalar(option_obj, bounds=(0.01, 3), method="bounded")

    ## A function to plot the chart based on change in days to expiry
    def plot_dte(self, dte_type):

        dte_dic = {"Week": 7, "Month": 31, "Quarter": 124,
                   "Six Months": 185, "Year": 365, "5 years": 1825}
        dte_op_lst = []
        dic_dte = {}

        for dte in dte_dic.values():
            self.days_to_expiry = dte
            self.calc_interest_rates()
            dte_op_lst.append(self.calc_option_value())

        if dte_type == "Continuous":
            dic_dte["Days to Expiry"] = dte_dic.values()
        else:
            dic_dte["Days to Expiry"] = dte_dic.keys()

        dic_dte["Black Scholes Option Price"] = dte_op_lst
        pd_dte = pd.DataFrame(dic_dte)
        ut.Utilities.plot_chart(pd_dte)

    ## A function to plot the charts based on change in interest rates
    def plot_interest_rates(self):

        r_list = np.arange(0, 0.14, 0.0025)
        r_op_list = []

        for i in r_list:
            self.interest_rates = i
            self.days_to_expiry = BSM.days_to_expiry
            r_op_list.append(self.calc_option_value())

        pd_r = pd.DataFrame(
            {"Interest rate": r_list,
             "Black Scholes Option Price": r_op_list}
        )
        ut.Utilities.plot_chart(pd_r)

    ## A function to plot the charts based on change in spot price
    def plot_spot_price(self):

        spot_lst = np.arange(self.spot_price*0.4,
                             self.spot_price*1.6, self.spot_price*0.05)
        intrinsic_val_lst = []
        spot_opt_lst = []
        var = self.__option_type()

        for i in spot_lst:
            self.spot_price = i
            intrinsic_val_lst.append(max(var*(i - self.strike_price), 0))
            spot_opt_lst.append(self.calc_option_value())

        pd_spot = pd.DataFrame(
            {"Black Scholes Option Price": spot_opt_lst,
             "Spot Price": spot_lst,
             "Intrinsic Value of Option": intrinsic_val_lst}
        )
        ut.Utilities.plot_chart(pd_spot)
    
## A function to plot the charts based on changes in Implied Volatility
    def plot_q2i(self):


        sigma_op_list = []
        sigma_list = np.arange(self.iv*1.05, self.iv*1.8, self.iv*0.05)
        
        for i in sigma_list:
            self.iv = i
            sigma_op_list.append(self.calc_option_value())

        pd_sigma = pd.DataFrame(
            {"Implied Volatility": sigma_list,
             "Black Scholes Option Price": sigma_op_list}
        )
        ut.Utilities.plot_chart(pd_sigma)
