# Option Pricing Model

### App url - https://dub.sh/ds

![image](https://user-images.githubusercontent.com/94735949/205714936-9cac193c-c253-4f59-bf9b-847d9a0e5c47.png)


This is an option pricing app based on legacy models like BSM and Garch(1,1) which takes in inputs like Days to expiry, Strike price, Spot price, Voltality etc to output the BSM calculated Option Price. It also used Garch(1,1) model to forecast option period volatility and draws comparison to Vix in order to assess the differences between the both. Based on the forecasted voltality trend, the app also builds a Iron condor hedging strategy to trade voltality and manage the risk.

### Tech Stack

![image](https://user-images.githubusercontent.com/94735949/205740646-4f0aad74-5a43-40de-85b1-1c20df6dbbfe.png) - Python

![image](https://user-images.githubusercontent.com/94735949/205740561-3a284c7f-cb4e-4e4a-b200-c39b7563dd17.png) - Streamlit

![image](https://user-images.githubusercontent.com/94735949/205740792-ebb3db44-7bd5-49ef-bfa1-dfd4ef6ec23f.png) - Git



*[While the trade date is fixed for this app, rest all parameters are flexible which makes the model valuable for a real life option price evaluation. This was initially done as a academic project by UCD Sumrfit Financial Data Science students, albeit the aim of the project is realised, owing to our flexible codebase we are positive that in further updates, with time, we can release more flexibilty for versatile use by all]*
