from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import database_URI
from sqlalchemy.ext.automap import automap_base
from datetime import datetime 
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = database_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)

@app.route('/')
def index():
    title = "Climate Analysis API"
    paragraphs = ["This API includes the following routes:"]
    list_items = ["Precipitation: \'/api/v1.0/precipitation\', documentation at \'/api/v1.0/precipitation/doc\'","Stations: \'/api/v1.0/stations\', documentation at \'/api/v1.0/stations/doc\'","Temperature Observations: \'/api/v1.0/tobs\', documentation at \'/api/v1.0/tobs/doc\'","Date range: \'/api/v1.0/<start>\' or \'/api/v1.0/<start>/<end>\', documentation at \'/api/v1.0/date_range/doc\'"]
    return render_template('index.html',title=title,paragraphs=paragraphs,list_items=list_items)

@app.route('/api/v1.0/precipitation')
def precipitation():
    return "test"

@app.route('/api/v1.0/precipitation/doc')
def precipitation_doc():
    return "test"

@app.route('/api/v1.0/stations')
def stations():
    return "test"

@app.route('/api/v1.0/stations/doc')
def stations_doc():
    return "test"

@app.route('/api/v1.0/tobs')
def tobs():
    return "test"

@app.route('/api/v1.0/tobs/doc')
def tobs_doc():
    return "test"

@app.route('/api/v1.0/date_range/doc')
def date_range_doc():
    return "test"


@app.route('/api/v1.0/<start>')
def start_date(start):
    return start

@app.route('/api/v1.0/<start>/<end>')
def date_range(start,end):
    return end


if __name__ == '__main__':
    app.run(debug=True)