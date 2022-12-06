## A class that can formulate hedged strategies for options
import Utilities as ut
import numpy as np
import pandas as pd
import datetime as dt


class OptionStrategyBuilder:

    def __init__(self, spot, vol):

        self.spot = spot
        self.forecasted_vol = vol

    ## Calculates the 1 standard deviation monthly basis and finds appropriate strike prices to be sold
    def __calc_monthly_vol(self):

        monthly_vol = (self.forecasted_vol * (22/252)**0.5)/100
        put_strike = round(self.spot*(1-monthly_vol)/10)*10
        call_strike = round(self.spot*(1+monthly_vol)/10)*10
        return call_strike, put_strike

    ## Returns mean of bid-ask of the option prices for given strike and type of option
    def __get_strikes_option_prices(self, strike, option_type):

        df_od = ut.Utilities.get_option_metric_data()
        df_od = df_od.loc[(df_od['Strike'] == strike) & (
            df_od["Put=1 Call=0"] == option_type)]
        df_od = df_od.loc[df_od["Open Interest"]
                          == df_od["Open Interest"].max()]
        return np.mean(df_od[['Bid Price', 'Ask Price']].values)

    def __get_SPX_data_on_expiry(self):

        file_path = ut.Utilities.getFilePath("SPX")
        df = pd.read_csv(file_path)
        df['Date'] = pd.TimedeltaIndex(
            df['Date'], unit='d') + dt.datetime(1899, 12, 30)
        return df.loc[df.Date == '2015-09-11', 'Close']

    def long_call(self, S, K, Price):
        # Long Call Payoff
        P = list(map(lambda x: max(x - K, 0) - Price, S))
        return P

    def long_put(self, S, K, Price):
        # Long Put Payoff
        P = list(map(lambda x: max(K - x, 0) - Price, S))
        return P

    def short_call(self, S, K, Price):
        # Payoff a shortcall is just the inverse of the payoff of a long call
        P = self.long_call(S, K, Price)
        return [-1.0*p for p in P]

    def short_put(self, S, K, Price):
        # Payoff a short put is just the inverse of the payoff of a long put
        P = self.long_put(S, K, Price)
        return [-1.0*p for p in P]

    ## Defines the iron condor strategy based on suitable strike selection and buying the wings of a strangle

    def ironcondor(self):

        S = np.arange(self.spot*0.8, self.spot*1.2, self.spot *
                      0.01)  # Get a list of spot prices
        # Get the desired strike and option prices based on forecasted volatility to make a strangle
        E1, E2 = self.__calc_monthly_vol()
        Price1 = self.__get_strikes_option_prices(E1, 0)
        Price2 = self.__get_strikes_option_prices(E2, 1)

        # Get strikes and option prices of the wings of a strangle to make ironcondor
        E3 = round((E1 + Price1 + Price2)/10)*10
        E4 = round((E2 - Price1 - Price2)/10)*10
        Price3 = self.__get_strikes_option_prices(E3, 0)
        Price4 = self.__get_strikes_option_prices(E4, 1)

        P_1 = self.short_call(S, E1, Price1)
        P_2 = self.short_put(S, E2, Price2)
        P_3 = self.long_call(S, E3, Price3)
        P_4 = self.long_put(S, E4, Price4)
        pd_os = pd.DataFrame({"Spot Price": S, "Iron Condor Payoff ($)": [
                             a+b+c+d for a, b, c, d in zip(P_1, P_2, P_3, P_4)]})
        ut.Utilities.plot_chart(pd_os)

        ## Iron Condor Implemetation: Value Tables

        close = self.__get_SPX_data_on_expiry()
        EP_1 = self.short_call(close, E1, Price1)
        EP_2 = self.short_put(close, E2, Price2)
        EP_3 = self.long_call(close, E3, Price3)
        EP_4 = self.long_put(close, E4, Price4)

        short_call_lst = [Price1, EP_1[0]]
        short_put_lst = [Price2, EP_2[0]]
        long_call_lst = [-Price3, EP_3[0]]
        long_put_lst = [-Price4, EP_4[0]]

        price_beg = Price1 + Price2 - Price3 - Price4
        price_expiry = EP_1[0]+EP_2[0]+EP_3[0]+EP_4[0]

        dict_pl = {"Short Call": short_call_lst, "Short Put": short_put_lst,
                   "Long Call": long_call_lst, "Long Put": long_put_lst, "Total": [price_beg, price_expiry]}

        return pd.DataFrame(dict_pl, index=['Cost($)', 'Value on expiry($)'])
