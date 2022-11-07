## class to initiate all our final results

### Need to think of a design pattern
from bsm import BSM

if __name__ == '__main__':
    days_to_expiry = int(input("Days to expiry: "))
    strike_price = int(input("Enter the strike price of the option: "))
    option_type = int(input("If call option enter 0, if put option enter 1:"))
    bsm = BSM(days_to_expiry, strike_price, option_type)
    print("The option value at expiry is:",bsm.calc_option_value())