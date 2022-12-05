# Option Pricing Model

### App url - https://dub.sh/ds

![image](https://user-images.githubusercontent.com/94735949/205714936-9cac193c-c253-4f59-bf9b-847d9a0e5c47.png)


This is an option pricing app based on legacy models like BSM and Garch(1,1) which takes in inputs like Days to expiry, Strike price, Spot price, Voltality etc to output the BSM calculated Option Price. It also used Garch(1,1) model to forecast option period volatility and draws comparison to Vix in order to assess the differences between the both. Based on the forecasted voltality trend, the app also builds a Iron condor hedging strategy to trade voltality and manage the risk.

### Tech Stack

![image](https://user-images.githubusercontent.com/94735949/205740646-4f0aad74-5a43-40de-85b1-1c20df6dbbfe.png) - Python

![image](https://user-images.githubusercontent.com/94735949/205740968-3d6514fc-eee9-4c6e-81fa-488309d8b1a3.png) - Streamlit

![image](https://user-images.githubusercontent.com/94735949/205741016-d14c8879-1b5a-4cbb-b605-eb53a0901720.png) - Git



*[While the trade date is fixed for this app, rest all parameters are flexible which makes the model valuable for a real life option price evaluation. This was initially done as a academic project by UCD Sumrfit Financial Data Science students, albeit the aim of the project is realised, owing to our flexible codebase we are positive that in further updates, with time, we can release more flexibilty for versatile use by all]*
