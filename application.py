from flask import Flask, session

# from config import Configuration
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
#
#
# app = Flask(__name__)
# # app.config.from_object(Configuration)
# app.config['SECRET_KEY'] = 'some_secret'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp\\finance.db'
# db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
#
#
# def format_value_float(value):
#     """Format value as USD."""
#     value = float(value)
#     return f"{value:,.2f}"
#
#
# def format_value_int(value):
#     """Format value as USD."""
#     value = int(value)
#     return f"{value:,}"
#
#
# app.jinja_env.globals.update(format_value_float=format_value_float,
#                              format_value_int=format_value_int)

app = Flask(__name__)


@app.route('/')
def index():
    return 'Якби все працює!'
