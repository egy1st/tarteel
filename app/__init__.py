import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# project configuration
app.config['SECRET_KEY'] = '1k_jh5jhgfj32lx-xghxl565LKHGHfgde__-236'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['AIRTABLE_API_KEY'] = 'keypZkU0Vtg72mTNN'

app.config['DEBUG'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models

