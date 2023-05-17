from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import os
from tfidfclassifier import start_prediction_tfidf
from bm25 import start_prediction_bm25
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
    catageory = db.Column(db.Text, nullable=False)
    originalText = db.Column(db.Text, nullable=False)
    userSummary= db.Column(db.Text, nullable=False)
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
    # uma = Summary(catageory= 'Yoga', 
    #                 originalText = 'प्राणायाम रोग निवारणको एक औषधि नै हो भन्दा पनि हुन्छ । दैनिक गरिने प्राणायामले मानिसको ७२ हजार नसामा रक्तप्रवाह राम्रो गराउन मद्दत गर्छ । यद्यपि प्राणायामका धेरै प्रकार छन् । तर यहाँ हामी ती प्राणायामको मात्र चर्चा गर्नेछौं । जसलाई बालबालिका, युवायुवती, वृद्धवृद्धा सबैले सहज रुपमा गर्न सक्छन् ।',
    #                 userSummary = 'प्राणायाम रोग निवारणको एक औषधि नै हो भन्दा पनि हुन्छ । दैनिक गरिने प्राणायामले मानिसको ७२ हजार नसामा रक्तप्रवाह राम्रो गराउन मद्दत गर्छ । यद्यपि प्राणायामका धेरै प्रकार छन् । तर यहाँ हामी ती प्राणायामको मात्र चर्चा गर्नेछौं । जसलाई बालबालिका, युवायुवती, वृद्धवृद्धा सबैले सहज रुपमा गर्न सक्छन् ।'
    #                 )
    # db.session.add(uma)
    # db.session.commit()

    # query = Summary.query.filter(Summary.id >= 5, Summary.id <= 7)

    # query = Summary.query.filter(Summary.id ==5)
    # query.delete(synchronize_session=False)
    # db.session.commit()


    return render_template('index.html')

@app.route('/test', methods=['POST'])
@cross_origin()
def add():
    # new_var = request.json['js file ma pathayako variable eg. new_var']
    original = request.json['originalText']
    userSummary = request.json['summary']
    category = request.json['category']
    userthresholdValue = float(request.json['thresholdValue'])
    
    tfidf_sum = start_prediction_tfidf(original, userthresholdValue)
    
    docsList = []
    records = Summary.query.filter_by(catageory = category).all()
    for record in records:
        docsList.append(record.userSummary)

    if len(docsList) == 0:
        return jsonify({"error" : "No such category data available","tfidf_sum" : tfidf_sum})
    bm25 = start_prediction_bm25(original, docsList, userthresholdValue)

    if userSummary != "":
        bm25_acc = calculate_accuracy(userSummary, bm25)
        tfidf_acc = calculate_accuracy(userSummary, tfidf_sum)

        record_taken = Summary.query.filter_by(originalText=original).all()

        if record_taken: 
            if userthresholdValue==0.9:   
                query = Summary.query.filter(Summary.id==record_taken[0].id)
                query.delete()
                db.session.commit()
                new_data = Summary(originalText=original,userSummary=userSummary, catageory=category)
                try:
                    db.session.add(new_data)
                    db.session.commit()
                except:
                    return 'Error Occured'
        else:
            new_data = Summary(originalText=original,userSummary=userSummary, catageory=category)
            try:
                db.session.add(new_data)
                db.session.commit()
            except:
                return 'Error Occured'
        
        return jsonify({"tfidf_sum" : tfidf_sum, "tfidf_acc": tfidf_acc,'bm25_sum' : bm25, 'bm25_acc' :bm25_acc})
        # new_data = Summary(originalText=original,userSummary=userSummary, tfidfModelSummary=tfidf_sum, tfidfacc= acc_tfids)

        

    return jsonify({"tfidf_sum" : tfidf_sum, 'bm25_sum' : bm25})

    

if __name__=='__main__':
    app.run(host="0.0.0.0", debug=True)


