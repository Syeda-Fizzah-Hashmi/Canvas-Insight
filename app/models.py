from datetime import datetime
from app import db


class Admin(db.Model):
    psyname = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))

    def __init__(self, psyname, email, password):
        self.psyname = psyname
        self.email = email
        self.password = password

    def __repr__(self):
        return '{},{}'.format(self.psyname, self.password)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    info = db.relationship('Information', backref='user', lazy='dynamic')
    reports = db.relationship('Report', backref='user', lazy='dynamic')


    def __repr__(self):
        return 'User: {}'.format(self.username)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(64))
    image = db.relationship('Image', backref='report', lazy='dynamic')

    def __repr__(self):
        return 'Report: {}'.format(self.id)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(64), default=None)
    image_url = db.Column(db.String(64), default=None)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

    def __repr__(self):
        return 'Image: {}'.format(self.id)

class Information(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(64))
    gender = db.Column(db.String(64))
    date = db.Column(db.Date)
    contact = db.Column(db.String(64))
    city = db.Column(db.String(64))
    history = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, patient_name, gender, date, contact, city, history):
        self.patient_name = patient_name
        self.gender = gender
        self.date = date
        self.contact = contact
        self.city = city
        self.history = history

    def __repr__(self):
        return '{}'.format(self.patient_name)
#db.drop_all()
#db.create_all()
