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

    ## Redefine volatility
    def __get_vol_interval(self):

        self.iv = np.arange(0.05,0.85,0.05)
    
    ## Calculate interval of option prices for given volatilities
    def calc_vol_interval(self):
        
        self.__get_vol_interval()
        vol_interval = self.calc_option_value()
        return  vol_interval

    ## Calculate delta of given option    
    def __get_delta(self):
        
        d1 = self.__get_d1()
        var = self.__option_type()
        delta = var*np.exp(-self.dividend *self.days_to_expiry/365) * ut.Utilities.N(var*d1)
        return delta
   
    ## Calculate gamma of given option    
    def __get_gamma(self):
        
        d1 = self.__get_d1()
        return np.exp(-self.dividend *self.days_to_expiry/365)  * ut.Utilities.N(d1) / (self.spot_price * self.iv * np.sqrt(self.days_to_expiry/365))
     
    def __get_interval(self, max_interval, grid_spacing):
         
        return np.arange(-max_interval, max_interval+grid_spacing, grid_spacing)
    
    ## Redefine spot price
    def __get_spotprice_interval(self, max_interval, grid_spacing):
    
        x = self.__get_interval(max_interval, grid_spacing)
        self.spot_price = (1+x)*self.spot_price
    
    ## Calculate interval of spotprices around given option
    def calc_spotprice_interval(self, max_interval, grid_spacing):
        
        self.__get_spotprice_interval(max_interval, grid_spacing)
        spot_interval = self.calc_option_value()
        return  spot_interval
    
    ## Calculate second-order polynomial approximation of option price wrt spot price of underlying
    def calc_ts_approx(self):
        
        delta = self.__get_delta()
        gamma = self.__get_gamma()
        x = self.__get_interval(0.3, 0.01)
        
        ts_approx_price = self.calc_option_value() + delta * (self.spot_price*x) + gamma * (self.spot_price*x)**2
        return ts_approx_price

    ## Redefine interest rate
    def __get_interest_interval(self):

        self.interest_rates = np.arange(0,0.14,0.0025)
    
    ## Calculate interval of option prices for given interest rates
    def calc_interest_interval(self):
        
        self.__get_interest_interval()
        interest_interval = self.calc_option_value()
        return  interest_interval

    ## Redefine days to maturity
    def __get_maturity_interval(self):

        self.days_to_expiry = np.array([7, 31, 124, 185, 365, 1825])
    
    ## Calculate interval of option prices for given time to maturities
    def calc_maturity_interval(self):
        
        init_dte = self.days_to_expiry
        self.__get_maturity_interval()
        maturity_interval = self.calc_option_value()
        self.days_to_expiry = init_dte
        return  maturity_interval

    ## A function to plot the charts based on change in volatility
    def plot_vol(self):

        vol_list = np.arange(0.05, 0.85, 0.05)
        self.calc_vol_interval()
        vol_op_list = self.calc_option_value()

        pd_vol = pd.DataFrame(
            {"Volatility": vol_list,
             "Black Scholes Option Price": vol_op_list}
        )
        self.calc_implied_vol()
        ut.Utilities.plot_chart(pd_vol)

    ## A function to plot the charts based on change in spot price
    def plot_ts_approximation(self):

        spot_lst = (1+self.__get_interval(0.3, 0.01))*self.spot_price

        ts_lst = self.calc_ts_approx()
        bs_lst = self.calc_spotprice_interval(0.3, 0.01)

        pd_ts = pd.DataFrame(
            {"Spot Price": spot_lst,
             "Black Scholes Option Price": bs_lst,
             "Taylor-Series Approximation": ts_lst}
        )
        self.calc_spotprice_SPX()
        ut.Utilities.plot_chart(pd_ts)

    ## A function to plot the chart based on change in days to expiry
    def plot_dte(self, dte_type):

        dte_dic = {"Week": 7, "Month": 31, "Quarter": 124,
                   "Six Months": 185, "Year": 365, "5 years": 1825}
        dte_op_lst = self.calc_maturity_interval()
        dic_dte = {}

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
        self.calc_interest_interval()
        r_op_list = self.calc_option_value()

        pd_r = pd.DataFrame(
            {"Interest rate": r_list,
             "Black Scholes Option Price": r_op_list}
        )
        self.calc_interest_rates()
        ut.Utilities.plot_chart(pd_r)

    ## A function to plot the charts based on change in spot price
    def plot_spot_price(self):

        spot_lst = (1+self.__get_interval(0.6, 0.05))*self.spot_price
        
        var = self.__option_type()
        intrinsic_val_lst = np.maximum(var*(spot_lst - self.strike_price),0)
        spot_opt_lst = self.calc_spotprice_interval(0.6, 0.05)  

        pd_spot = pd.DataFrame(
            {"Black Scholes Option Price": spot_opt_lst,
             "Spot Price": spot_lst,
             "Intrinsic Value of Option": intrinsic_val_lst}
        )
        self.calc_spotprice_SPX()
        ut.Utilities.plot_chart(pd_spot)
