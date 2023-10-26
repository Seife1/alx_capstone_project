"""This file is needed to indicate that your directory is a Python package."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = 'c1df51c66f1102f931b9abf2900499f9'

# Configuring MySQL DB connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0913158716@localhost/blogpage'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# Creating SQLAlchemy instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'unsuccess'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seife4033@gmail.com'
app.config['MAIL_PASSWORD'] = 'h z a w e m m v n p m w p a e u'
mail = Mail(app)



# # Initializing Flask app with SQLAlchemy 
# db.init_app(app)

migrate = Migrate(app, db)

from blog import routes
