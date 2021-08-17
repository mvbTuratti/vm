from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b2baeaddeb849ed2171fa67c3cbfb6f7'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'root_app'
login_manager.login_message_category = 'info'

from app import routes