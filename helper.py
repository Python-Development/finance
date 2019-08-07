from application import app
import requests


def format_value_float(value):
    """Format value as USD."""
    value = float(value)
    return f"{value:,.2f}"


def format_value_int(value):
    """Format value as USD."""
    value = int(value)
    return f"{value:,}"


app.jinja_env.globals.update(format_value_float=format_value_float, format_value_int=format_value_int)


def lookup(symbol, ind=0):
    key = ['zbKmuWlMBw567VPijVFF7ZsPIRO3lw7CLJC45ktVQOataVhwtUf1aL65h0lZ',
           'xARckomzGL6rXBCD8XAuwBsYWpGymkLLzf4ezRtk5NFKt6Nz5IKhm1xnxrn6',
           '11IL0BGRBH4kDe3wHo6cAi8esm2SkTazFYATIhHmYLCA4brujDFJ12ezxV3v',
           'Jy32UwC6XcYDcjJZZTfmT9tUYGqhV2i792ctRuPJkzQ8nNoICm4UxNUqBCaX',
           'zrYQyYc4HAvWRUZ6GVP4C5lKh6W00IVu5PfZ1Uao3Gr34R4cyGjQOfM4mKFB',
           'L8v5E6HZfj6NrTvLfM6AcV3y2qGuKgVBUelASregYhhVcaDY9gL7SHvOZmLk',
           'VFWKqQhAP2kdiFlZLH38jgY6ftYyUHrobBLyRyod29QFdlIR4NV7SVRLuhyN',
           'a32PExYLTjv3F0TR3v1eCyA8oPs4MP7Wm07Sd2Ii6WQbj4yc0FZ1f2zkuiaQ']
    try:
        requests.get(f'https://api.worldtradingdata.com/api/v1/stock?symbol={symbol}'
                     f'&api_token={key[ind]}').json()['data'][0]['symbol']
    except (KeyError, TypeError, ValueError):
        if len(key) > ind + 1:
            return lookup(symbol, ind + 1)
        else:
            return requests.get(f'https://api.worldtradingdata.com/api/v1/stock?symbol={symbol}'
                                f'&api_token={key[ind]}').json()
    try:
        get = requests.get(f'https://api.worldtradingdata.com/api/v1/stock?symbol={symbol}&api_token={key[ind]}').json()
        return {
            'companyName': get['data'][0]['name'],
            'currency': get['data'][0]['currency'],
            'symbol': get['data'][0]['symbol'],
            'price': float(get['data'][0]['price']),
            'day_change': abs(float(get['data'][0]['day_change'])),
            'change_pct': abs(float(get['data'][0]['change_pct'])),
            'close_yesterday': get['data'][0]['close_yesterday'],
            'price_open': get['data'][0]['price_open'],
            'day_high': get['data'][0]['day_high'],
            'day_low': get['data'][0]['day_low'],
            'market_cap': get['data'][0]['market_cap'],
            'volume': get['data'][0]['volume'],
            'volume_avg': get['data'][0]['volume_avg'],
            'shares': int(get['data'][0]['shares']),
            'color_high_low': 'red' if float(get['data'][0]['day_change']) < 0 else 'green',
            'symbol_high_low': False if float(get['data'][0]['day_change']) < 0 else True}
    except (KeyError, TypeError, ValueError):
        return 'sorry'


def look_price(symbol, ind=0):
    key = ['R4EQOXXl72So1LGEeRwiuCll2xygPLcwEvlQzcVQkTmQowesOB20EillvlWo',
           'xARckomzGL6rXBCD8XAuwBsYWpGymkLLzf4ezRtk5NFKt6Nz5IKhm1xnxrn6',
           '11IL0BGRBH4kDe3wHo6cAi8esm2SkTazFYATIhHmYLCA4brujDFJ12ezxV3v',
           'Jy32UwC6XcYDcjJZZTfmT9tUYGqhV2i792ctRuPJkzQ8nNoICm4UxNUqBCaX',
           'zrYQyYc4HAvWRUZ6GVP4C5lKh6W00IVu5PfZ1Uao3Gr34R4cyGjQOfM4mKFB',
           'L8v5E6HZfj6NrTvLfM6AcV3y2qGuKgVBUelASregYhhVcaDY9gL7SHvOZmLk',
           'VFWKqQhAP2kdiFlZLH38jgY6ftYyUHrobBLyRyod29QFdlIR4NV7SVRLuhyN',
           'a32PExYLTjv3F0TR3v1eCyA8oPs4MP7Wm07Sd2Ii6WQbj4yc0FZ1f2zkuiaQ']
    try:
        requests.get(f'https://api.worldtradingdata.com/api/v1/stock?symbol={symbol}'
                     f'&api_token={key[ind]}').json()['data'][0]['symbol']
    except (KeyError, TypeError, ValueError):
        return look_price(symbol, ind + 1)
    get = requests.get(f'https://api.worldtradingdata.com/api/v1/stock?symbol={symbol}&api_token={key[ind]}').json()
    return {'price': float(get['data'][0]['price'])}
