#coding: utf-8
from flask import Flask
from flask.ext.pymongo import PyMongo

# Init flask app
restApp = Flask(__name__)
restApp.config.from_object('config')

# Init mongodb instance
mongo = PyMongo(restApp)

# Init views
from .views import *
