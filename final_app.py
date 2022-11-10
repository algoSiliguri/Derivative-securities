import streamlit as st
import BlackScholesModel as bs
import Utilities as ut

###sidebar

#sidebar title

st.sidebar.write("Here is your control panel")
st.sidebar.info('Trade date : 12/08/2015', icon="ℹ️")

#sidebar parameters

days_to_expiry = st.sidebar.slider("Days to Expiry", value=31, min_value=7, max_value=100)
strike_price = st.sidebar.number_input("Enter a strike price for your option (750-2500)", min_value=750, max_value=2500, step=10)
if strike_price not in ut.Utilities.get_strike_prices():
        st.sidebar.error("Strike price not in given data!!! Please renter!!!")
        st.stop()
option_type = st.sidebar.radio("Select your option type - Call-> 0 | Put-> 1",(0,1))
bs.BSM.check_iv = st.sidebar.checkbox("Select to check IV",value = False)

## Get the BSM object 
bsm = bs.BSM(days_to_expiry, strike_price, option_type)

if bs.BSM.check_iv:
    bsm.iv = st.sidebar.slider("Implied volatility", min_value = 0.01, max_value = 2.000, step = 0.001)


###main_section
#title

st.title("Options Pricing model")
st.subheader("Derivative Securities Project - Group 15")

col1, col2, col3, col4, col5 = st.columns(5)  

with col1:
    bsm.calc_interest_rates()
    st.metric("Interest rate (%)",round(bsm.interest_rates*100,3))

with col2:
    st.metric("Dividend Yield (%)",1.903)

with col3:
    if bs.BSM.check_iv:
        st.metric("Find IV", round(bsm.iv,3))
    else:
        bsm.calc_implied_vol()
        st.metric("Options IV", round(bsm.iv,3))

with col4:
    st.metric("BSM Option Price ($)",round(bsm.calc_option_value(),2))

with col5:
    st.metric("Given option price ($)", bsm.get_price())