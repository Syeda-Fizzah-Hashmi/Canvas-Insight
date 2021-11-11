from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, DateTimeField, SelectField
from wtforms.validators import DataRequired, EqualTo
from app import images
import datetime

class UploadForm(FlaskForm):
    username = StringField('Username')
    image = FileField('Drawing Image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])
    submit = SubmitField('Analyse')

class DeleteForm(FlaskForm):
    patient_name = StringField('Patient Name')
    submit = SubmitField('Delete')

class RegistrationForm(FlaskForm):
    psyname = StringField('Name', validators=[DataRequired()])
    email = StringField('Email Address',validators=[DataRequired()])
    password = PasswordField('New Password', validators=[
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password',validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    admin_name = StringField('Name', validators=[DataRequired()])
    admin_password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class PatientForm(FlaskForm):
    patient_name = StringField('patient_name', validators=[DataRequired()])
    gender = SelectField('Gender', choices = [('Male', 'male'),('Female','female'),('Other','other')],
        validators=[DataRequired()] )  
    date = DateTimeField(
        "Date", format="%Y-%m-%d",
        default=datetime.datetime.now(), ## Now it will call it everytime.
        validators=[DataRequired()]
    )
    contact = StringField('Contact #', validators=[DataRequired()])
    city = SelectField('City', choices = [('Karachi', 'Karachi'),('Lahore', 'Lahore'),('Islamabad', 'Islamabad')
        ,('Faisalabad', 'Faisalabad'),('Rawalpindi', 'Rawalpindi'),('Peshawar', 'Peshawar'),('Sialkot', 'Sialkot'),('Multan', 'Multan')])  
    history = TextAreaField('Medical History')

    submit = SubmitField('Save')









