import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

file_path = os.path.abspath(os.getcwd()) + "/shorturl/instance/db.sqlite3"

app = Flask(__name__)
app.secret_key = 'sdlalgharidalsdD'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + file_path

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

db = SQLAlchemy(app)
db.init_app(app)
