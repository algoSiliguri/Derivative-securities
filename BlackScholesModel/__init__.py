import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
import numpy as np
import Utilities as ut
import datetime as dt
import Garch as ga

class BSM:
    check_iv = False
    bsm_option_price = 0

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
        self.option_premium = 0
        self.option_payoff = 0
        self.sum_transaction_costs = 0
        self.total_pnl = 0

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

    ## Calculate delta of given option
    def __get_delta(self):

        d1 = self.__get_d1()
        var = self.__option_type()
        delta = var*np.exp(-self.dividend *
                           self.days_to_expiry/365) * ut.Utilities.N(var*d1)
        return delta

    ## Calculate gamma of given option
    def __get_gamma(self):

        d1 = self.__get_d1()
        return np.exp(-self.dividend * self.days_to_expiry/365) * ut.Utilities.N(d1) / (self.spot_price * self.iv * np.sqrt(self.days_to_expiry/365))

    ## Calculate interval of spotprices around given option
    def __calc_spotprice_interval(self):

        x = np.arange(-0.3, 0.31, 0.01)
        self.spot_price = (1+x)*self.spot_price
        spot_interval = self.calc_option_value()
        return spot_interval

    ## Calculate second-order polynomial approximation of option price wrt spot price of underlying
    def __calc_ts_approx(self):

        delta = self.__get_delta()
        gamma = self.__get_gamma()
        x = np.arange(-0.3, 0.31, 0.01)

        ts1_approx_price = self.calc_option_value() + delta * (self.spot_price*x)
        ts2_approx_price = self.calc_option_value() + delta * (self.spot_price*x) + gamma * (self.spot_price*x)**2/2
        return ts1_approx_price, ts2_approx_price

    ## Get SPX data from '12/08/2015' to Expiry
    def __get_SPX_data_to_expiry(self):

        file_path = ut.Utilities.getFilePath("SPX")
        df = pd.read_csv(file_path)
        df['Date'] = pd.TimedeltaIndex(
            df['Date'], unit='d') + dt.datetime(1899, 12, 30)
        df_SPX = df.loc[(df['Date'] >= pd.Timestamp(2015, 8, 12) )
        & (df['Date'] < pd.Timestamp(2015, 8, 12)+dt.timedelta(days=self.days_to_expiry+1))]
        return df_SPX

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
        init_dte = self.days_to_expiry
        init_ir = self.interest_rates

        for dte in dte_dic.values():
            self.days_to_expiry = dte
            self.calc_interest_rates()
            dte_op_lst.append(self.calc_option_value())

        self.days_to_expiry = init_dte
        self.interest_rates = init_ir

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
        init_ir = self.interest_rates

        for i in r_list:
            self.interest_rates = i
            r_op_list.append(self.calc_option_value())

        self.interest_rates = init_ir

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
        init_sp = self.spot_price

        for i in spot_lst:
            self.spot_price = i
            intrinsic_val_lst.append(max(var*(i - self.strike_price), 0))
            spot_opt_lst.append(self.calc_option_value())

        self.spot_price = init_sp
        pd_spot = pd.DataFrame(
            {"Black Scholes Option Price": spot_opt_lst,
             "Spot Price": spot_lst,
             "Intrinsic Value of Option": intrinsic_val_lst}
        )
        ut.Utilities.plot_chart(pd_spot)

    ## A function to plot the charts based on changes in Implied Volatility
    def plot_q2i(self):

        sigma_op_list = []
        sigma_list = np.arange(0.05, 0.85, 0.05)
        init_iv = self.iv

        for i in sigma_list:
            self.iv = i
            sigma_op_list.append(self.calc_option_value())

        self.iv = init_iv

        pd_sigma = pd.DataFrame(
            {"Implied Volatility (Percent)": sigma_list * 100,
             "Black Scholes Option Price": sigma_op_list}
        )
        ut.Utilities.plot_chart(pd_sigma)

    ## A function to plot the charts based on change in spot price
    def plot_ts_approximation(self):

        init_spot = self.spot_price
        spot_lst = (1+np.arange(-0.3, 0.31, 0.01))*self.spot_price

        ts_lst = self.__calc_ts_approx()
        bs_lst = self.__calc_spotprice_interval()

        self.spot_price = init_spot
        self.calc_option_value()

        pd_ts = pd.DataFrame(
            {"Spot Price": spot_lst,
             "Black Scholes Option Price": bs_lst,
             "1st-Order Taylor-Series Approximation": ts_lst[0],
             "2nd-Order Taylor-Series Approximation": ts_lst[1]}
        )
        ut.Utilities.plot_chart(pd_ts)

    def __calc_ask_price(self):
        
        df_od = ut.Utilities.get_option_metric_data()

        df_od = df_od.loc[(df_od['Strike'] == self.strike_price) & (df_od['Put=1 Call=0'] == self.call_or_put)]
        df_ask = df_od.loc[df_od["Open Interest"] == df_od["Open Interest"].max()]
        ask_price = df_ask.iloc[0,5]
        return ask_price

    def __calc_option_payoff(self):
        
        var = self.__option_type()
        if type(self.spot_price) is float:
            return max(var*(self.spot_price-self.strike_price), 0)
        elif type(self.spot_price) is np.ndarray:
            return max(var*(self.spot_price[-1]-self.strike_price), 0)

    ## Calculate delta for each of the days up to expiry
    def calc_hedged_portfolio(self, vol_type, trans_costs):

        init_dte = self.days_to_expiry
        init_spot = self.spot_price
        init_vol = self.iv

        if vol_type == "Forecast Volatility":
            garch = ga.Garch()
            self.iv = garch.calc_ann_forecast_vol()/100

        df_SPX = self.__get_SPX_data_to_expiry().reset_index(drop=True)
        self.spot_price = df_SPX.iloc[:,5].values
        self.days_to_expiry = (dt.timedelta(days=self.days_to_expiry)+pd.Timestamp(2015,8,12)-df_SPX['Date'])/dt.timedelta(days=1)
        self.option_payoff = self.__calc_option_payoff()
        
        delta_to_expiry = self.__get_delta()
        
        stock_holdings = delta_to_expiry*self.spot_price
        change_holdings = delta_to_expiry.diff()
        change_holdings.iloc[0] = delta_to_expiry.iloc[0]

        val_shares_bought = change_holdings*self.spot_price
        val_shares_bought.iloc[-1] = val_shares_bought.iloc[-1]+stock_holdings.iloc[-1]
        
        self.option_premium = self.__calc_ask_price()
        txn_cost = abs(val_shares_bought)*trans_costs + self.option_premium*trans_costs
    
        cumulative_pnl = np.zeros(len(delta_to_expiry))
        bank = np.zeros(len(delta_to_expiry))
        bank[0] = self.option_premium - (val_shares_bought[0] + txn_cost[0])
        cumulative_pnl[0] = bank[0] + stock_holdings[0]
        
        for i in range(1, len(self.days_to_expiry)):
            bank[i] = bank[i-1]*np.exp(self.interest_rates*(self.days_to_expiry.values[i]-self.days_to_expiry.values[i-1])/365) - (val_shares_bought[i] + txn_cost[i])
            cumulative_pnl[i] = bank[i]+stock_holdings.values[i]
        cumulative_pnl[-1] = cumulative_pnl[-1] - self.option_payoff + stock_holdings.values[-1]
        
        df_delta = pd.DataFrame(data = [self.days_to_expiry, delta_to_expiry, self.spot_price, stock_holdings, val_shares_bought, txn_cost, cumulative_pnl])
        df_delta.index = ['DTE', 'Delta', 'Spot Price ($)', 'Stock Holdings ($)', 'Shares Bought ($)', 'Trans. Cost ($)', 'Cum. P&L ($)']
        df_delta = df_delta.transpose()
        df_delta['DTE'] = -df_delta['DTE'].astype(int)
        df_delta = df_delta.reset_index(drop=True)

        self.sum_transaction_costs = np.sum(txn_cost)
        self.total_pnl = df_delta['Cum. P&L ($)'].iloc[-1]

        self.days_to_expiry = init_dte
        self.spot_price = init_spot
        self.iv = init_vol

        return df_delta