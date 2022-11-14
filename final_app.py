import streamlit as st
import BlackScholesModel as bs
import Utilities as ut

###sidebar

#sidebar title

st.sidebar.write("Here is your control panel")
st.sidebar.info('Trade date : 12/08/2015', icon="ℹ️")

#sidebar parameters

days_to_expiry = st.sidebar.slider(
    "Days to Expiry", value=31, min_value=7, max_value=100)

option_type = st.sidebar.radio(
    "Select your option type - Call-> 0 | Put-> 1", (0, 1))

strike_price = st.sidebar.number_input(
    "Enter a strike price for your option (750-2500)", min_value=750, max_value=2500, value=2080, step=10)

if strike_price not in ut.Utilities.get_strike_prices(option_type):
    st.sidebar.error("Strike price not in given data!!! Please renter!!!")
    st.stop()

bs.BSM.check_iv = st.sidebar.checkbox("Brent's Volatility Solver")


bsm = bs.BSM(days_to_expiry, strike_price, option_type)

### Main_section ###
#title

st.title("Options Pricing model")
st.subheader("Derivative Securities Project - Group 15")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    bsm.calc_interest_rates()
    st.metric("Interest rate (%)", round(bsm.interest_rates * 100, 3))

with col2:
    bsm.calc_dividend()
    st.metric("Dividend Yield (%)", round(bsm.dividend * 100, 3))

with col3:
    bsm.calc_spotprice_SPX()
    st.metric("SPX Spot Price", round(bsm.spot_price, 2))

with col4:
    bsm.calc_implied_vol()
    st.metric("Given Option IV", round(bsm.iv, 3))

with col5:
    bsm.calc_option_value()
    st.metric("BSM Option Price($)", round(bs.BSM.bsm_option_price, 3))

with col4:
    if bs.BSM.check_iv:
        bsm.imp_vol_solver()
        st.metric("Calculated Option IV", round(bsm.brent_iv, 3))

with col5:
    if bs.BSM.check_iv:
        st.metric("Given Option Price($)", round(bsm.mid_bid_ask, 3))
