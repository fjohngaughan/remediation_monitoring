import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess...'
    SQLALCHEMY_DATABASE_URI = 'postgres://eebpdvnqyhkrzf:facee458508103e87641807380e78c786f1043780f766caa473cdc06ea8ee27e@ec2-34-206-8-52.compute-1.amazonaws.com:5432/d2j5rn153cv6fv' or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True