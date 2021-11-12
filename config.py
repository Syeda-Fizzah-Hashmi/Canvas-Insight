import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'triple-a-b-is-awesome'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'app/static/img/')
    UPLOADS_DEFAULT_URL = 'http://localhost:5000/static/img/'
    
    UPLOADED_IMAGES_DEST = os.path.join(basedir, 'app/static/img/')
    UPLOADED_IMAGES_URL = 'http://localhost:5000/static/img/'