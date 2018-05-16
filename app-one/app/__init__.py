#!/usr/bin/python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.secret_key = "top secret"

from app import routes, models
