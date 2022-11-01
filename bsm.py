## Class to to initialise inputs to a Black Scholes Model

import pandas as pd
from scipy.interpolate import interp1d
from utilities import Utilities

class BSM:

    def __init__(self, days_to_expiry):

        self.days_to_expiry = days_to_expiry
        self.interest_rates = 0
        self.dividend = 0
        self.iv = 0
    
    ## Calculating ineterest rates from zero curve using linear interpolation
    def calc_interest_rates(self):

        file_path = Utilities.getCurrDir() + "/project/ZeroCurve.csv"
        df = pd.read_csv(file_path)
        df_data = df.loc[df['Date'] == '12/08/2015']
        X = df_data['Days']
        Y = df_data['Rate']

        interpolate_x = self.days_to_expiry
        y_interp = interp1d(X,Y)
        self.interest_rates = y_interp(interpolate_x)


bsm = BSM(int(input("Days to expiry: ")))
bsm.calc_interest_rates()
print(bsm.interest_rates)