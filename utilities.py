## Class for using any utility function, mostly contains static method

import os

class Utilities:
    
    @staticmethod
    def getCurrDir():
        return os.getcwd()


