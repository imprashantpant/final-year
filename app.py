from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import os
from tfidfclassifier import start_prediction_tfidf
from accuracycalculator import calculate_accuracy
from sqlalchemy.sql import func
basedir = os.path.abspath(os.path.dirname(__file__))

# WSGI Application
# Provide template folder name
# The default folder name should be "templates" else need to mention custom folder name
app = Flask(__name__, template_folder='templatesFiles', static_folder='staticFiles')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #gender = db.Column(db.String[50], nullable=False)
    originalText = db.Column(db.Text, nullable=False)
    userSummary= db.Column(db.Text, nullable=False)
    tfidfModelSummary = db.Column(db.Text, nullable=False)
    tfidfacc = db.Column(db.Float, nullable=False)
    # add new column to table here

    def __repr__(self):
        return '<Text>' + str(self.id);

# @app.route('/')
# def welcome():
#     return "This is the home page of Flask Application"

@app.route('/')
@cross_origin()
def index():
    datas = Summary.query.all()
    return render_template('index.html')

@app.route('/test', methods=['POST'])
@cross_origin()
def add():
    # new_var = request.json['js file ma pathayako variable eg. new_var']
    original = request.json['originalText']
    userSummary = request.json['summary']
    tfidf_sum = start_prediction_tfidf(original)

    acc_tfids = calculate_accuracy(userSummary, tfidf_sum)
    new_data = Summary(originalText=original,userSummary=userSummary, tfidfModelSummary=tfidf_sum, tfidfacc= acc_tfids)

    try:
        db.session.add(new_data)
        db.session.commit()

    except:
        return 'Error Occured'

    return jsonify({"tfidf_sum" : tfidf_sum, "acc_tfids" : acc_tfids})

if __name__=='__main__':
    app.run(host="0.0.0.0", port=port)


