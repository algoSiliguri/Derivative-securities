import pandas as pd
import Utilities as ut
from arch import arch_model
import numpy as np
import datetime as dt

class Garch:

    def __init__(self):

        self.ann_forcast_vol=0
        self.ann_realised_vol=0
        self.vix=0

    ## Fetch train data from the SPX csv file
    def get_spx_data(self):
        file_path = ut.Utilities.getFilePath("SPX")
        df = pd.read_csv(file_path)
        df['Date'] = pd.TimedeltaIndex(df['Date'], unit='d') + dt.datetime(1899, 12, 30)
        df = df.set_index('Date')
        train_data = df.loc[: pd.Timestamp(2015, 8, 12)]
        train_data['Log_Return'] = np.log(train_data['Adj Close']).diff().mul(100)
        train_data = train_data.dropna()
        return train_data['Log_Return']

    ## Define the garch model
    def garch_1_1(self):
        model = arch_model(self.get_spx_data(), p = 1, q = 1, mean = 'constant', vol = 'GARCH', dist = 'normal')
        return model.fit(update_freq=5)
    

    ## Calculate the annualised forecasted voltality for historic returns
    def calc_ann_forecast_vol(self):
        model_result = self.garch_1_1()
        timefactor = 252/len(model_result.conditional_volatility)
        self.ann_forcast_vol = np.sqrt(timefactor*sum(model_result.conditional_volatility))
        return self.ann_forcast_vol

    ## Calculate the annualised forecasted voltality for option period
    def calc_ann_realised_vol(self):
        model_result = self.garch_1_1()
        self.forecasts = model_result.forecast(horizon=31, reindex=False)
        df_forecast = pd.DataFrame(self.forecasts.variance[-1:])
        df_forecast = df_forecast.transpose()
        ut.Utilities.plot_chart(df_forecast)
        self.ann_realised_vol = np.sqrt((252/31)*(np.sum(df_forecast[pd.Timestamp(2015, 8, 12)])))
        return self.ann_realised_vol

    ## Fetch vix voltality from the vix file
    def calc_vix_vol(self):
        file_path = ut.Utilities.getFilePath("VIX")
        df = pd.read_csv(file_path)
        df['Date'] = pd.TimedeltaIndex(df['Date'], unit='d') + dt.datetime(1899, 12, 30)
        df = df.set_index('Date')
        self.vix = df.loc[pd.Timestamp(2015, 8, 12)]
        self.vix = self.vix['Adj Close']
        return self.vix
