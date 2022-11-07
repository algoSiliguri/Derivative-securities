import streamlit as st
from bsm import BSM
from utilities import Utilities
import sys



###sidebar

#sidebar title

st.sidebar.write("Here is your control panel")
st.sidebar.info('Trade date : 12/08/2015', icon="ℹ️")

#sidebar parameters

days_to_expiry = st.sidebar.slider("Days to Expiry", value=31, min_value=7, max_value=100)
strike_price = st.sidebar.number_input("Enter a strike price for your option (750-2500)", min_value=750, max_value=2500)
if strike_price not in Utilities.get_strike_prices():
        st.sidebar.error("Strike price not in given data!!! Please renter")
        st.stop()
option_type = st.sidebar.radio("Select your option type - Call-> 0 | Put-> 1",(0,1))


bsm = BSM(days_to_expiry, strike_price, option_type)

###main_section
#title

st.title("Options Pricing model")
st.subheader("Derivative Securities Project - Group 15")

col1, col2, col3, col4 = st.columns(4)  

with col1:
    #BSM.calc_interest_rates(days_to_expiry)
    bsm.calc_interest_rates()
    st.metric("Interest rate (%)",round(bsm.interest_rates,5))

with col2:
    st.metric("Dividend Yield (%)",1.903)

with col3:
    #BSM.calc_option_value()
    st.metric("Option Price ($)",round(bsm.calc_option_value(),5),3)

with col4:
    st.metric("Bid-ask spread",10,2)