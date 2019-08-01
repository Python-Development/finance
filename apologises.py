def user_error():
    return 'Sorry, your access is refused because the user with this username dose not exist.'


def password_error():
    return 'Sorry, your access is refused because the password you entered is invalid.'


def name_is_used():
    return 'Sorry, this username is already in use. Please choose another username.'


def symbol_error():
    return 'Sorry, this symbol is not in use. Please select the correct symbol.'


def not_enough_shares():
    return 'Sorry, but you want to sell more shares than you have. Please make a valid request.'


def not_enough_cash(number, symbol):
    share = 'share' if number == 1 else 'shares'
    return f"Sorry, but you don't have enough cash to buy {number} {share} of {symbol}. Please make a valid request."


def error_key():
    return "Sorry, API key is wrong. Please make a valid request."
