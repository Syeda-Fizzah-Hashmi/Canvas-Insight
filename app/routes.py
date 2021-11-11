from flask import Flask, render_template, flash, redirect, url_for, request, session
from app import app, db, images
from app.forms import UploadForm, RegistrationForm, LoginForm, PatientForm, DeleteForm
from app.models import User, Report, Image, Admin, Information
from app.predict import TFLiteObjectDetection
import json, PIL
from passlib.hash import sha256_crypt
import gc, os
from app.depression_classification import score_depression, depression_classification

#pip install passlib
#pip install flask-wtf

#extraaaa
from app.model import Yolov4
import torch
from torch import nn
import torch.nn.functional as F
from app.utils import *
from app.models import Image
import ast


@app.route('/application_request', methods = ['GET', 'POST'])
def handle_request():
    if request.method == 'POST':
        if request.files:
            username = 'app'

            filename = images.save(request.files['image'])
            url = images.url(filename)

            #---------------------

            result = predict(filename)

            #---------------------

            user = User.query.filter_by(username = username).first()
            if user is None: user = User(username = username)

            report = Report(user = user, data = json.dumps(result))

            image = Image(report = report)

            image.image_filename = filename
            image.image_url = url

            db.session.add(user)
            db.session.add(report)
            db.session.add(image)

            db.session.commit()

            return 'Report Generated'
        return 'No Files Recieved'
    return 'Method not POST'


@app.route('/signin', methods=['GET','POST'])
def Login_page():
    try:
        form = LoginForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                record = Admin.query.filter_by(psyname = form.admin_name.data).first()
                if record:
                    admin = str(record).split(',')
                    if sha256_crypt.verify(form.admin_password.data, admin[1]):
                        session['psyname'] = admin[0]

                        print('admin logged in', flush = True)
                        return redirect(url_for('dashboard'))
            else:
                flash('Invalid Credentials, Login In failed','error')
                return redirect(url_for('Login_page'))
        return render_template("signin.html", title = 'Sign In', form=form)
    
    except Exception as e:
        return(str(e))


@app.route('/', methods=['GET','POST'])
def register_page():
    try:
        form = RegistrationForm()
        if request.method == 'POST':
            print('post data Recieved (^^)', flush=True)
            if form.validate_on_submit():
                psyname  = form.psyname.data
                email = form.email.data
                password = sha256_crypt.encrypt((str(form.password.data)))

                admin = Admin(psyname=psyname, email=email, password=password)
                print('Admin created:', flush = True)
                print(admin, flush = True)

                if len(Admin.query.filter_by(psyname=psyname).all()):
                    flash('Username is alredy taken', 'error')
                    return redirect(url_for('register_page'))
                else:
                    db.session.add(admin)

                    db.session.commit()  

                    gc.collect()

                    session['psyname'] = psyname
                    return redirect(url_for('dashboard'))
            
            else:
                if(not form.psyname.data or not form.email.data or not form.password.data):
                    flash('Fields must not be empty', 'error')
                else:
                    flash('Both passwords should match', 'error')
                    return redirect(url_for('register_page'))

        return render_template("register.html", title = 'Register', form=form)
    except Exception as e:
        return(str(e))


@app.route('/index')
def index():
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            username = request.form.get('patient')
            category = request.form.get('category')

            #app.config['UPLOADED_IMAGES_DEST'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/img/'+category+'/')
            #app.config['UPLOADED_IMAGES_URL'] = 'http://localhost:5000/static/img/'+category+'/'

            filename = images.save(request.files['image'])
            url = images.url("prediction.jpg")

            #---------------------

            result = predict(filename, category = category)
            print(result[1])
            #---------------------

            user = User.query.filter_by(username = username).first()
            if user is None: user = User(username = username)

            report = Report(user = user, data = json.dumps(str(result[1])), category = category)

            image = Image(report = report)
            url = images.url(str(filename)+'_predictions.jpg')

            image.image_filename = filename
            image.image_url = url

            db.session.add(user)
            db.session.add(report)
            db.session.add(image)

            db.session.commit()

            flash('User Report for username: {} generated. '.format(username), 'success')
            return redirect(url_for('report', report_id = report.id))
        else:
            flash('Report was not generated.', 'error')
            return redirect(url_for('upload'))

    return render_template('upload.html', title = 'Upload', form = form, patients=Information.query.all())

@app.route('/report/<report_id>', methods=['GET', 'POST'])
def report(report_id):      
    report = Report.query.get(report_id)
    data = json.loads(report.data)
    image = report.image.first()
  
    #find depression score
    score=score_depression(ast.literal_eval(data), report.category)
    diagnosis=depression_classification(score)


    user_report = {
        'username': report.user.username,
        'data': ast.literal_eval(data),
        'image_url': image.image_url,
        'image_filename': image.image_filename,
        'score':score,
        'diagnosis':diagnosis
        }
    return render_template('report.html', title = 'Report', report = user_report)


@app.route('/user/<user_id>')
def user(user_id):
    user = User.query.get(user_id)
    reports = user.reports.all()
    return render_template('user.html', title = 'User', username = user.username, reports = reports, information=Information.query.filter_by(patient_name=user.username).first())


@app.route('/delete_patient', methods=['GET', 'POST'])
def Delpatient():
    form = DeleteForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = request.form.get('patient')
            print(name, flush=True)
            return redirect(url_for('delete', patientName = name))

    return render_template('delete.html', title = 'Delete', form = form, patients=Information.query.all())

@app.route('/delete_patient/<patientName>')
def delete(patientName):
    patient = Information.query.filter_by(patient_name=patientName)
    
    if patient:
        # Patient Information
        print('Delete Personal Information', flush=True)
        patient.delete()
        print(Information.query.all(), flush=True)

        # Users data
        user = User.query.filter_by(username=patientName).first()
        id = user.id
        User.query.filter_by(username=patientName).delete()
        print('Delete user record', flush=True)
        print(User.query.all(), flush=True)

        # If had any test reports 
        if Report.query.filter_by(user_id = id):
            for rep in Report.query.filter_by(user_id = id).all():
                R_id = rep.id
                Report.query.filter_by(id=R_id).delete()
                Image.query.filter_by(report_id=R_id).delete()
            print('Delete test reports')

        db.session.commit()
        print('Successful deletion of {}'.format(patientName), flush=True)
        flash('Patient: {}, is successfully deleted'.format(patientName), 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Failed to delete Patient: {}'.format(patientName), 'error')
        return redirect(url_for('Delpatient'))

@app.route('/patient_info', methods=['GET', 'POST'])
def PatientPage():
    try:
        form = PatientForm()
        if request.method == 'POST':
           
            if form.validate_on_submit():
                patient_name  = form.patient_name.data
                gender = form.gender.data
                date = form.date.data
                contact = form.contact.data
                city = form.city.data
                history = form.history.data

                if Information.query.filter_by(patient_name=patient_name).first():
                    flash('Patient is already added', 'error')
                    return redirect(url_for('PatientPage'))

                #if Information.query.all():
                #    new_id = len(Information.query.all())+1
                #else:
                #    new_id =1

                patient = Information(patient_name=patient_name, gender=gender, date=date, contact=contact, city=city, history=history)
                db.session.add(patient)
                db.session.commit()

                print(Information.query.all(), flush=True)

                flash('Patient: {} data is successfully entered! '.format(form.patient_name.data), 'success')
                return redirect(url_for('upload'))
            else:
                flash('Failed to save record','error')
                return redirect(url_for('PatientPage'))

        return render_template("addPatient.html", title = 'Patient Information', form=form)
    except Exception as e:
        return(str(e))


@app.route('/dashboard')
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', title = 'Dashboard', users = users, total_patients = len(users), total_reports = len(Report.query.all()), admin = session['psyname'])

@app.route('/about')
def about():
    return render_template('about.html', title = 'About')

def predict(image_filename, category):
    MODEL_FILENAME = 'models/'+category+'/Yolov4_epoch50.pth'
    LABELS_FILENAME = 'models/'+category+'/_classes.txt'
    
    print(MODEL_FILENAME, flush= True)
    #with open(LABELS_FILENAME, 'r') as f:
    #    labels = [l.strip() for l in f.readlines()]
    #od_model = TFLiteObjectDetection(MODEL_FILENAME, labels)

    num_classes = len(open(LABELS_FILENAME).readlines(  ))
    print(num_classes, flush= True)

    model = Yolov4(n_classes=num_classes)
    pretrained_dict = torch.load(MODEL_FILENAME, map_location=torch.device('cpu'))
    model.load_state_dict(pretrained_dict)
    model.eval()
    img = PIL.Image.open('app/static/img/' + image_filename).convert('RGB')
    
    sized = img.resize((608, 608))
    # Ammara
    boxes = do_detect(model, sized, 0.5, num_classes,0.4)
    class_names = load_class_names(LABELS_FILENAME)
    result_array=plot_boxes(img, boxes, 'app/static/img/'+str(image_filename)+'_predictions.jpg', class_names)
    print(result_array)
    return result_array



