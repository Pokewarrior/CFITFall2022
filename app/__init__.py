from flask import Flask
from flask_bootstrap import Bootstrap

# New imports
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# force loading of environment variables
load_dotenv('.flaskenv')

# Get the environment variables from .flaskenv
# Google Cloud SQL (change this accordingly)
# Get the environment variables from .flaskenv
USERNAME="access"
PASSWORD=""
PROJECT_ID ="Cfit"
INSTANCE_NAME ="cfitdata"
DB_IP="34.145.150.163"
DB_NAME="CFITD"

app = Flask(__name__)

app.secret_key = "scsu_cfit"
app.config["SECRET_KEY"] = "scsu_cfit"
# SQL Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{DB_IP}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

# Create database connection and associate it with the Flask application
db = SQLAlchemy(app)

login = LoginManager(app)

# enables @login_required
login.login_view = 'login'

# Add models
from app import routes, models
from app.models import user, admin


# Create admin and basic user account
user_check = user.query.filter_by(username='admin').first()
if user_check is None:
    user_admin = user(username='admin', email='admin@SCSUCFIT', role='admin')
    user_admin.set_password('csc400sum22')
    db.session.add(user_admin)
    db.session.commit()

user_check = user.query.filter_by(username='instructor').first()
if user_check is None:
    user_instructor = user(username='instructor', email='instructor@SCSUCFIT', role = 'instructor')
    user_instructor.set_password('csc400sum22')
    db.session.add(user_instructor)
    db.session.commit()
