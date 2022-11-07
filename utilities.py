## Class for using any utility function, mostly contains static method

import os
from jproperties import Properties


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
