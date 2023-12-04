from datetime import timedelta
from flask import Flask

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'abcdefghijklmn'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # cookies在7天后过期
