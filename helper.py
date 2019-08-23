from application import app
import requests

api_url = 'https://api.worldtradingdata.com/api/v1/stock?symbol={}&api_token={}'
api_keys = ['zbKmuWlMBw567VPijVFF7ZsPIRO3lw7CLJC45ktVQOataVhwtUf1aL65h0lZ',
            'xARckomzGL6rXBCD8XAuwBsYWpGymkLLzf4ezRtk5NFKt6Nz5IKhm1xnxrn6',
            '11IL0BGRBH4kDe3wHo6cAi8esm2SkTazFYATIhHmYLCA4brujDFJ12ezxV3v',
            'Jy32UwC6XcYDcjJZZTfmT9tUYGqhV2i792ctRuPJkzQ8nNoICm4UxNUqBCaX',
            'zrYQyYc4HAvWRUZ6GVP4C5lKh6W00IVu5PfZ1Uao3Gr34R4cyGjQOfM4mKFB',
            'L8v5E6HZfj6NrTvLfM6AcV3y2qGuKgVBUelASregYhhVcaDY9gL7SHvOZmLk',
            'VFWKqQhAP2kdiFlZLH38jgY6ftYyUHrobBLyRyod29QFdlIR4NV7SVRLuhyN',
            'a32PExYLTjv3F0TR3v1eCyA8oPs4MP7Wm07Sd2Ii6WQbj4yc0FZ1f2zkuiaQ',
            'R4EQOXXl72So1LGEeRwiuCll2xygPLcwEvlQzcVQkTmQowesOB20EillvlWo',
            'xARckomzGL6rXBCD8XAuwBsYWpGymkLLzf4ezRtk5NFKt6Nz5IKhm1xnxrn6']

key_ind = 0


def inc_key_ind():
    global key_ind
    key_ind = key_ind + 1 % len(api_keys)


def format_value_float(value):
    """Format value as USD."""
    value = float(value)
    return f"{value:,.2f}"


def format_value_int(value):
    """Format value as USD."""
    value = int(value)
    return f"{value:,}"


app.jinja_env.globals.update(format_value_float=format_value_float, format_value_int=format_value_int)


def lookup(symbol):
    try:
        r_count = 0
        while True:
            app.logger.info("Call API for key={} and symbol={}".format(key_ind, symbol))
            r = requests.get(api_url.format(symbol, api_keys[key_ind]))
            if r.status_code != 200:
                return {"error": "sorry, worldtradingdata api wasn't reponded code={}".format(r.status_code)}
            j_data = r.json()
            error = ""
            if "message" in j_data:
                error = j_data["message"]
            if "Message" in j_data:
                error = j_data["Message"]
            if error:
                app.logger.warning("Call API error".format(error))
                if error.find("API") >= 0:
                    inc_key_ind()
                    r_count += 1
                    if r_count < len(api_keys):
                        continue
                return {"error": "sorry, worldtradingdata api error={}".format(error)}

            rs_count = int(j_data["symbols_returned"])
            if rs_count == 0:
                return {"error": "sorry, symbol {} was not found".format(symbol)}

            data = j_data["data"][0]
            if data["symbol"].upper() != symbol.upper():
                return {"error": "sorry, symbol {} has wrong data".format(symbol)}

            return {
                'companyName': data['name'],
                'currency': data['currency'],
                'symbol': data['symbol'],
                'price': float(data['price']),
                'day_change': abs(float(data['day_change'])),
                'change_pct': abs(float(data['change_pct'])),
                'close_yesterday': data['close_yesterday'],
                'price_open': data['price_open'],
                'day_high': data['day_high'],
                'day_low': data['day_low'],
                'market_cap': data['market_cap'],
                'volume': data['volume'],
                'volume_avg': data['volume_avg'],
                'shares': int(data['shares']),
                'color_high_low': 'red' if float(data['day_change']) < 0 else 'green',
                'symbol_high_low': False if float(data['day_change']) < 0 else True}
    except Exception as exc:
        app.logger.error("API error: {}".format(repr(exc)))
        return {"error": "sorry, api call raise error {}".format(repr(exc))}


def look_price(symbol):
    resp = lookup(symbol)
    if "error" in resp:
        return {"error": resp["error"]}
    if "price" not in resp:
        return {"error": "symbol {} has no price value".format(symbol)}
    return {'price': resp['price']}
