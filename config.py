import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess...'
    SQLALCHEMY_DATABASE_URI = 'postgres://igeqpwwqvxgurd:a12322967b1b7f9ff3a69e767a73fba1a5f04487b9743097eebf91c202b78740@ec2-3-217-219-146.compute-1.amazonaws.com:5432/d14ap4jj8k91hr' or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True