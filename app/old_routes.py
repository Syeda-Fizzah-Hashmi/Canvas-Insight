from flask import render_template, flash, redirect, url_for, request
from app import app, db, images
from app.forms import UploadForm
from app.models import User, Report, Image
from app.predict import TFLiteObjectDetection
import json, PIL

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

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            username = form.username.data

            filename = images.save(request.files['image'])
            # reads from static/imgs
            url = images.url("prediction.jpg")

            #---------------------

            result = predict(filename)
            print(result[1])
            #---------------------

            user = User.query.filter_by(username = username).first()
            if user is None: user = User(username = username)

            report = Report(user = user, data = json.dumps(str(result[1])))


            image = Image(report = report)
            url = images.url(str(filename)+'_predictions.jpg')

            image.image_filename = filename
            image.image_url = url

            db.session.add(user)
            db.session.add(report)
            db.session.add(image)

            db.session.commit()

            flash('User Report for username: {} generated. '.format(form.username.data), 'success')
            return redirect(url_for('report', report_id = report.id))
        else:
            flash_errors(form)
            flash('ERROR! Report was not generated.', 'error')

    return render_template('upload.html', title = 'Upload', form = form)

@app.route('/report/<report_id>', methods=['GET', 'POST'])
def report(report_id):      
    report = Report.query.get(report_id)
    data = json.loads(report.data)
    image = report.image.first()

    #find depression score
    #score=score_depression(ast.literal_eval(data))
    #diagnosis=depression_classification(score)
    score = 0.3
    diagnosis = 'hmmm'


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
    return render_template('user.html', title = 'User', username = user.username, reports = reports)

@app.route('/dashboard')
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', title = 'Dashboard', users = users)

@app.route('/about')
def about():
    return render_template('about.html', title = 'About')

def predict(image_filename, category):
    MODEL_FILENAME = 'model.tflite'
    LABELS_FILENAME = 'labels.txt'
    
    with open(LABELS_FILENAME, 'r') as f:
        labels = [l.strip() for l in f.readlines()]
    od_model = TFLiteObjectDetection(MODEL_FILENAME, labels)
    
    model = Yolov4(n_classes=16)
    pretrained_dict = torch.load("Yolov4_epoch50 (1).pth", map_location=torch.device('cpu'))
    model.load_state_dict(pretrained_dict)
    model.eval()
    img = PIL.Image.open('app/static/img/' + image_filename).convert('RGB')
    
    sized = img.resize((608, 608))
    # Ammara
    boxes = do_detect(model, sized, 0.5, 16,0.4)
    class_names = load_class_names("_classes.txt")
    result_array=plot_boxes(img, boxes, 'app/static/img/'+str(image_filename)+'_predictions.jpg', class_names)
    print(result_array)
    return result_array



def score_depression(my_dict):
    depression_score = 0
    print(type(my_dict))
    
    if "door" in my_dict: 
        del my_dict['door'] 
    else: 
        depression_score+=0.125

    if "wall" in my_dict : 
        del my_dict['wall'] 
    else: 
        depression_score+=0.125

    if "roof" in my_dict : 
        del my_dict['roof'] 
    else: 
        depression_score+=0.125

    if "closed_window" in my_dict : 
        del my_dict['closed_window'] 
    else: 
        depression_score+=0.125
    
    if "single_line_roof" in my_dict :depression_score+=0.05
    
    if  "wall" in my_dict :depression_score+=0.05
    
    if "door" in my_dict :depression_score+=0.05
    
    if "closed_window" in my_dict :depression_score+=0.05
    
    if "open_window" in my_dict :depression_score+=0.05
    
    if "roof" in my_dict :depression_score+=0.05
    
    if "shadow" in my_dict :depression_score+=0.05
    
    if "chimney" in my_dict :depression_score+=0.05
    
    if "smoking_chimney" in my_dict :depression_score+=0.05
    
    if "clouds" in my_dict :depression_score+=0.05
    
    if "shaded_roof" in my_dict :depression_score+=0.05
    
    if "big_house" in my_dict :depression_score+=0.05
    
    if  "small_house" in my_dict :depression_score+=0.05
    
    if "bottom_placed_house" in my_dict : depression_score+=0.05
    
    print(depression_score)

    return depression_score


def depression_classification(score):
  if score < 0.3:
    return 'No Depression'
  elif score < 0.5:
    return 'Mild Depression'
  elif score < 0.7:
    return 'Moderate Depression'
  elif score >= 0.7:
    return 'Severe Depression'