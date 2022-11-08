## Class for using any utility function, mostly contains static method

import os
from jproperties import Properties
import pandas as pd


class Utilities:

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
    def get_strike_prices():

        file_path = Utilities.getFilePath("iv")
        df = pd.read_csv(file_path)
        df = df.loc[(df['Trade dAte'] == '12/08/2015') & (df["Put=1 Call=0"] == 0)]
        df.loc[:, 'Strike x 1000'] = df['Strike x 1000'].div(1000)
        return [i for i in df['Strike x 1000']]