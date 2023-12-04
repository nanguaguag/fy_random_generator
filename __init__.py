from datetime import timedelta
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefghijklmn'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # cookies在7天后过期
app.config['STATIC_URL_PATH'] = '/'
