## Class for using any utility function, mostly contains static method

import os
from jproperties import Properties
import pandas as pd
from scipy.stats import norm


class Utilities:

    ## A static method to fetch option metric data
    @staticmethod
    def get_option_metric_data():

        file_path = Utilities.getFilePath("iv")
        df = pd.read_csv(file_path)
        df_od = df.loc[(df['Trade dAte'] == '12/08/2015') &
                       (df["Implied Vol"] != -99.99)].copy()
        df_od.loc[:, 'Strike x 1000'] = df_od['Strike x 1000'].div(1000)
        df_od = df_od.rename(columns={"Strike x 1000": "Strike"})
        df_od = df_od.reset_index()
        del df_od['index']
        return df_od

    ## A static method to get the file path for the csv
    @staticmethod
    def getFilePath(sub_path):

        configs = Utilities.read_properties()
        file_path = os.getcwd() + configs.get(sub_path).data
        return file_path

    #### A static method to read the environment properties file ####
    @staticmethod
    def read_properties():

        configs = Properties()

        with open('env.properties', 'rb') as read_prop:
            configs.load(read_prop)

        return configs

## A static method to get given strike prices from data
    @staticmethod
    def get_strike_prices(option_type):

        df_od = Utilities.get_option_metric_data()
        df_od = df_od.loc[df_od['Put=1 Call=0'] == option_type]
        return [i for i in df_od['Strike']]

    ## A static method to return normal distribution cdf
    @staticmethod
    def N(x):

        return norm.cdf(x)
