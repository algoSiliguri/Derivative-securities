% Black Scholes Merton Formula in Matlab

function [ cprice, delta, gamma ] = blackScholesCallPrice( K, T, S0, r, y, sigma )
numerator = log(S0./K) + (r-y+0.5*sigma.^2).*T;
denominator = sigma.*sqrt(T);
d1 = numerator./denominator;
d2 = d1 - denominator;
cprice = S0 *exp(-y*T).* normcdf(d1) - exp(-r.*T).*K.*normcdf(d2);
delta = normcdf(d1);
gamma = normpdf(d1) ./ (S0.*denominator);

end