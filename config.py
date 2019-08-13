import os

db_uri = 'sqlite:///tmp/finance.db' if not os.getenv("DATABASE_URL") else \
"postgres://ayvshjjvsooovk:2f3141ff1ad9a3add571d026c7159eb0ba2303fd05ad600da3bff7e37f3df4e4@ec2-75-101-133-29.compute-1.amazonaws.com:5432/db28vta3s61r16"


class Configuration(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = db_uri
    SECRET_KEY = 'some_secret'
