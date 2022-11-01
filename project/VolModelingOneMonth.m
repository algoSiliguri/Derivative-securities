%
% Sample script to load daily returns; GARCH(1,1) model volatility
% and compare to the VIX and future realised vol.
%
% Richard J. McGee (richard.mcgee@ucd.ie)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%*******************!Set Dates Here!***************************************
tradeDate = datenum('22122011','ddmmyyyy');
%                   ~~~~~~~~~~
expiryDate = datenum('19012012','ddmmyyyy');
%                   ~~~~~~~~~~

%*************!Set Sample Size for GARCH Fitting Here!*********************
S = 1000; % the number of previous returns used to fit the GARCH model
%   ~~~~

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% Load S&P500 data
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sp500 = csvread('SPXDaily1950.csv',1);
indexdates = x2mdate(sp500(:,1));
index = sp500(:,6);
rm =log(index(2:end)./index(1:end-1));
sp500Dates = indexdates(2:end);
%
fprintf('************************************************************* \n');
fprintf('Loaded Daily S&P500 data from %s to %s \n', ...
    datestr(min(sp500Dates)),datestr(max(sp500Dates)));

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% Load VIX data
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
VIX = csvread('VIX.csv',1);
vixDates = x2mdate(VIX(:,1));
VIX = VIX(:,6);

fprintf('************************************************************* \n');
fprintf('Loaded VIX data from %s to %s \n', ...
    datestr(min(vixDates)),datestr(max(vixDates)));
fprintf('************************************************************* \n');

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% Select Garch(1,1)
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ToEstMdl = garch(1,1); % tells Matlab what model to estimate

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% index using provided dates and create correct return samples
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
d1 = find(sp500Dates == tradeDate);
d2 = find(sp500Dates <= expiryDate,1,'last');
d3 = find(vixDates == tradeDate);
% historical returns up to the forecast date to estimate the GARCH model
ret_h  = rm(d1-(S-1):d1);
% realised returns over the following month (being forecast)
ret_r  = rm(d1+1:d2);nRets = numel(ret_r);
% calculate the 'future' realised vol the model is trying to forecast
timeFactor = 252/nRets; %(to annualise the variance)
realisedVol = sqrt(sum(ret_r.^2)*timeFactor); 
% Estimate a GARCH(1,1)
fprintf('Fitting GARCH Model:\n');
EstMdl = estimate(ToEstMdl,ret_h);

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% Variance sums over time - sum variance forecasts, convert to annualised
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
forecastVariance = sum(forecast(EstMdl,nRets,'Y0',ret_h)); % monthly variance
forecastVol = (timeFactor*forecastVariance).^0.5; % annualised vol
vixVol = VIX(d3);

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% Print the results
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
fprintf('************************************************************* \n');
fprintf('GARCH(1,1) forecast Vol: %.2f \n', 100*forecastVol);
fprintf('************************************************************* \n');
fprintf('VIX: %.2f \n', vixVol);
fprintf('************************************************************* \n');
fprintf('Realised Vol: %.2f \n', 100*realisedVol);
fprintf('************************************************************* \n');
