clear;
K =1420;
TC = 1e-4;
dt = 1/365;
% Time to expiry on each date to expiry
timeToExp =[30;29;28;25;23;22;21;18;17;16;15;14;11;10;9;8;7;3;2;1;0]/365;
%Index on each date to expiry

St = [1419.829956;1418.099976;1402.430054;1426.189941;...
      1462.420044;1459.369995;1466.469971;1461.890015;...
      1457.150024;1461.020020;1472.119995;1472.050049;...
      1470.680054;1472.339966;1472.630005;1480.939941;...
      1485.979980;1492.560059;1494.810059;1494.819946;...
      1502.959961];
  
subplot(2,1,1),plot(St); hold all; plot(0*St+K);title('Index Level');
axis([-inf,inf,-inf,inf]); grid on;
r = 0.005;
y=0.02;
Ca = 27.1;
IV = 0.17598;
N = numel(St)-1;
deltah = zeros(N-1,1);
fprintf('------------------------------------------------------------------\n');
fprintf('Delta Hedging \n');
fprintf('------------------------------------------------------------------\n');

% Call premium

CallPremium = Ca * (1-TC);

BankBalance = CallPremium;
stockCosts=0;
% Get the vector of delta positions
for t =1:N
    S0 = St(t);
    t2e = timeToExp(t);
    [ ~, deltah(t), ~ ] = blackScholesCallPrice( K, t2e, S0, r, y, IV ); 
    if t>1
        oldStockPosition = deltah(t-1);
    else
        oldStockPosition = 0;
    end
    amtBuy = (deltah(t)-oldStockPosition)*St(t);
    stockCosts = amtBuy +abs(amtBuy)*TC;
    BankBalance = BankBalance*exp(r*dt) - stockCosts;

    fprintf(' t= %i; delta = %.2f; bought $ %.2f of the index; Bank $ %.2f \n', t,deltah(t),amtBuy,BankBalance);
   
end

subplot(2,1,2),plot(deltah(1:end));
axis([-inf,inf,-inf,inf]); grid on;
title('Delta Position');
fprintf('------------------------------------------------------------------\n');

CallPayoff = max(0,St(end)-K);
profit = deltah(end)*St(end) +BankBalance - CallPayoff;

fprintf('Total Hedge Profit: $ %.2f \n', profit);
fprintf('------------------------------------------------------------------\n');




