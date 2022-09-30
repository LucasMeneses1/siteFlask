from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
import cloudinary
import os

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
cloudinary.config(cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"), api_key=os.environ.get("CLOUDINARY_API_KEY"), api_secret=os.environ.get("CLOUDINARY_API_SECRET"))

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'


from comunidadedev import routes