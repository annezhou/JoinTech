import logging
import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, render_template, request, url_for, escape
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, TextAreaField
from pprint import pprint
import datetime, time
from utils.email_client import send_email

app = Flask(__name__, static_folder='static/assets')
# logging.basicConfig(filename='email_client.log',level=logging.DEBUG,
#                     format='%(asctime)s %(message)s')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hacktech'
app.config['UPLOAD_FOLDER'] = '/home/potato/resumes'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(120))
    lname = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    age = db.Column(db.Boolean)
    grade = db.Column(db.String(40))
    school = db.Column(db.String(120))
    busorigin = db.Column(db.String(80))
    webdev = db.Column(db.Boolean)
    mobiledev = db.Column(db.Boolean)
    arvrdev = db.Column(db.Boolean)
    hardwaredev = db.Column(db.Boolean)
    aidev = db.Column(db.Boolean)
    website = db.Column(db.String(80))
    linkedin = db.Column(db.String(80))
    poem = db.Column(db.Text)
    techsimplify = db.Column(db.Text)
    hacktechsuggest = db.Column(db.Text)
    othercomment = db.Column(db.Text)
    accept_tos = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)
    resumepath = db.Column(db.String(120))

    def __init__(self, fname, lname, email, age, grade, school, busorigin, webdev, mobiledev, arvrdev, hardwaredev, aidev, website, linkedin, poem, techsimplify, hacktechsuggest, othercomment, accept_tos, timestamp, resumepath):
        '''
        initialize the user database.
        things that should be stored:
        first name, last name, school, grade
        transportation, which bus if any
        interested in: web dev, mobile dev, AR/VR, hardware, AI/ML, other
        resume file
        links to github, linkedin, portfolio
        over 18 by march 3, 2017?
        acrostic poem based around the word "ROSE"
        something you did today that could have been enhanced by tech
        cool things you'd like to see at hacktech
        questions/comments/concerns
        do you accept MLH code of conduct?
        '''
        self.fname           = fname
        self.lname           = lname
        self.email           = email
        self.age             = age
        self.grade           = grade
        self.school          = school
        self.busorigin       = busorigin
        self.webdev          = webdev
        self.mobiledev       = mobiledev
        self.arvrdev         = arvrdev
        self.hardwaredev     = hardwaredev
        self.aidev           = aidev
        self.website         = website
        self.linkedin        = linkedin
        self.poem            = poem
        self.techsimplify    = techsimplify
        self.hacktechsuggest = hacktechsuggest
        self.othercomment    = othercomment
        self.accept_tos      = accept_tos
        self.timestamp       = timestamp
        self.resumepath      = resumepath
        

    def __repr__(self):
        return self.fname + ' ' + self.lname + ' ' + self.email + ' ' + str(self.age) + ' ' + self.grade + ' ' + self.school + ' ' + self.busorigin + ' ' + str(self.webdev) + ' ' + str(self.mobiledev) + ' ' + str(self.arvrdev) + ' ' + str(self.hardwaredev) + ' ' + str(self.aidev) + ' ' + self.website + ' ' + self.linkedin + ' ' + self.poem + ' ' + self.techsimplify + ' ' + self.hacktechsuggest + ' ' + self.othercomment + ' ' + str(self.accept_tos) + ' ' + str(self.timestamp) + ' ' + self.resumepath

class RegistrationForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=120), validators.DataRequired()])
    lname = StringField('Last Name', [validators.Length(min=1, max=120), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=120), validators.Email(), validators.DataRequired()])
    age = BooleanField('Age')
    grade = StringField('Grade', [validators.DataRequired()])
    school = StringField('School/University', [validators.DataRequired()])
    busorigin = StringField('Bus Origin')
    webdev = BooleanField('Web Development')
    mobiledev = BooleanField('Mobile Development')
    arvrdev = BooleanField('AR/VR Development')
    hardwaredev = BooleanField('Hardware Development')
    aidev = BooleanField('AI Development')
    website = StringField('Website')
    linkedin = StringField('LinkedIn Profile')
    poem = TextAreaField('Question 1: Poem')
    techsimplify = TextAreaField('Question 2: Simplify Something With Technology')
    hacktechsuggest = TextAreaField('Question 3: Suggestions for Hacktech')
    othercomment = TextAreaField('Question 4: Questions/Comments/Concerns')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        if 'resumefileinput' not in request.files:
            return str(request.files)
        f = request.files['resumefileinput']
        resumepath = os.path.join(app.config['UPLOAD_FOLDER'], str(time.time()))
        user = User(form.fname.data, form.lname.data, form.email.data, form.age.data, form.grade.data, form.school.data, form.busorigin.data, form.webdev.data, form.mobiledev.data, form.arvrdev.data, form.hardwaredev.data, form.aidev.data, form.website.data, form.linkedin.data, form.poem.data, form.techsimplify.data, form.hacktechsuggest.data, form.othercomment.data, form.accept_tos.data, datetime.datetime.utcnow(), resumepath)
        f.save(resumepath)
        db.session.add(user)
        db.session.commit()
        # Now we'll send the email application confirmation
        subject = "Thanks for Applying to Hacktech 2017!"
        html = render_template('Hacktech2017_submitapplication.html')
        send_email(user.email, subject, html)

        return "Thank you for registering, "+escape(form.fname.data)+". We've sent a confirmation link to "+escape(form.email.data)+"."
    elif request.method == 'POST':
        return "There was a problem with your registration information.\nPlease check your information and try again."
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run()
