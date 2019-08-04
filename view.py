from flask import render_template, redirect, url_for, flash, request
from application import app, db, session
from model import User, Share, History
from werkzeug.security import generate_password_hash, check_password_hash
from application import login_manager, login_required, login_user, current_user
import requests
import apologises as error
import forms as form
import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    update()
    user = User.query.filter_by(username=session['user_name']).first()
    total = sum(i.total for i in user.shares) + user.cash
    return render_template('index.html', shares=user.shares, cash=user.cash, total=total)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = form.LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                session['user_name'] = user.username
                flash('You were successfully logged in')
                login_user(user)
                return redirect(url_for('index'))
            return render_template('apologise.html', error=error.password_error())
        else:
            return render_template('apologise.html', error=error.user_error())
    return render_template('login.html', form=login_form, alert='primary')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login_form = form.LoginForm()
    register_form = form.RegisterForm()
    if register_form.validate_on_submit():
        # db.create_all()
        user = User.query.filter_by(username=register_form.username.data).first()
        if user:
            return render_template('apologise.html', error=error.name_is_used())
        hashed_password = generate_password_hash(register_form.password.data, method='sha256')
        new_user = User(username=register_form.username.data, password=hashed_password, cash=10000)
        db.session.add(new_user)
        db.session.commit()
        flash("Success! Let's log in")
        return render_template('login.html', form=login_form)
    return render_template('register.html', form=register_form)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/quote', methods=['GET', 'POST'])
def quote():
    quote_form = form.QuoteForm()
    if quote_form.validate_on_submit():
        data = lookup(quote_form.symbol.data)
        try:
            return render_template(
                'quoted.html',
                companyName=data.get('companyName'),
                currency=data.get('currency'),
                symbol=data.get('symbol'),
                price=data.get('price'),
                day_change=abs(float(data.get('day_change'))),
                change_pct=abs(float(data.get('change_pct'))),
                close_yesterday=data.get('close_yesterday'),
                price_open=data.get('price_open'),
                day_high=data.get('day_high'),
                day_low=data.get('day_low'),
                market_cap=data.get('market_cap'),
                volume=data.get('volume'),
                volume_avg=data.get('volume_avg'),
                shares=int(data.get('shares')),
                color_high_low='red' if float(data.get('day_change')) < 0 else 'green',
                symbol_high_low=False if float(data.get('day_change')) < 0 else True)
        except (KeyError, TypeError, ValueError):
            return render_template('apologise.html', error=error.symbol_error())

    return render_template('quote.html', form=quote_form)


@app.route('/buy', methods=['GET', 'POST'])
def buy():
    buy_form = form.BuyForm()
    if buy_form.validate_on_submit():
        symbol = buy_form.symbol.data
        data = lookup(symbol)
        user = User.query.filter_by(username=session['user_name']).first()
        try:
            for item in user.shares:
                if (user.cash - (float(data.get('price')) * buy_form.number.data)) < 0:
                    return render_template('apologise.html',
                                           error=error.not_enough_cash(buy_form.number.data, symbol.upper()))
                if item.symbol == symbol.upper():
                    item.number += buy_form.number.data
                    item.total += float(data.get('price')) * buy_form.number.data
                    user.cash -= float(data.get('price')) * buy_form.number.data
                    new_history = History(
                        symbol=item.symbol,
                        name=item.name,
                        number=buy_form.number.data,
                        price=data.get('price'),
                        total=float(data.get('price')) * buy_form.number.data,
                        transacted=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                        status='bought',
                        owner=user)
                    db.session.add(new_history)
                    db.session.commit()
                    flash('Success')
                    return redirect(url_for('index'))
            new_shares = Share(
                symbol=data.get('symbol'),
                name=data.get('companyName'),
                number=buy_form.number.data,
                price=data.get('price'),
                total=float(data.get('price')) * buy_form.number.data,
                owner=user)
            new_history = History(
                symbol=new_shares.symbol,
                name=new_shares.name,
                number=new_shares.number,
                price=new_shares.price,
                total=new_shares.total,
                transacted=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                status='bought',
                owner=user)
            user.cash -= float(data.get('price')) * buy_form.number.data
            db.session.add(new_shares, new_history)
            db.session.commit()
            flash('Success')
            return redirect(url_for('index'))
        except (KeyError, TypeError, ValueError):
            return render_template('apologise.html', error=error.symbol_error())
    return render_template('buy.html', form=buy_form)


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    sell_form = form.SellForm()
    user = User.query.filter_by(username=session['user_name']).first()
    if sell_form.validate_on_submit():
        symbol = request.form.get('symbol')
        data = look_price(symbol)
        if not symbol:
            return render_template('apologise.html', error=error.symbol_error())
        for item in user.shares:
            if item.symbol == symbol.upper():
                if item.number - sell_form.number.data < 0:
                    return render_template('apologise.html', error=error.not_enough_shares())
                item.number -= sell_form.number.data
                item.total -= float(data.get('price')) * sell_form.number.data
                user.cash += float(data.get('price')) * sell_form.number.data
                new_history = History(
                    symbol=item.symbol,
                    name=item.name,
                    number=sell_form.number.data,
                    price=data.get('price'),
                    total=float(data.get('price')) * sell_form.number.data,
                    transacted=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                    status='sold',
                    owner=user)
                db.session.add(new_history)
                db.session.commit()
                if item.number == 0:
                    Share.query.filter(Share.symbol == item.symbol).delete()
                    db.session.commit()
                flash('Success')
                return redirect(url_for('index'))
    return render_template('sell.html', form=sell_form, choice=user.shares)


@app.route('/history', methods=['GET', 'POST'])
def history():
    user = User.query.filter_by(username=session['user_name']).first()
    return render_template('history.html', history=user.history)


@app.route('/apologise')
def apologise():
    return render_template('apologise.html')


def update():
    user = User.query.filter_by(username=session['user_name']).first()
    for share in user.shares:
        price = look_price(share.symbol).get('price')
        share.price = price
        share.total = float(price) * share.number
        db.session.commit()
    return None


def lookup(symbol, ind=0):
    key = ['xARckomzGL6rXBCD8XAuwBsYWpGymkLLzf4ezRtk5NFKt6Nz5IKhm1xnxrn6',
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
        return lookup(symbol, ind + 1)
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
    key = ['xARckomzGL6rXBCD8XAuwBsYWpGymkLLzf4ezRtk5NFKt6Nz5IKhm1xnxrn6',
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
