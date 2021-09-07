from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import database_URI
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from flask_cors import CORS
from sqlalchemy import func, desc


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = database_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route('/')
def index():
    title = "Climate Analysis API"
    paragraphs = ["This API includes the following routes:"]
    list_items = ["Precipitation: \'/api/v1.0/precipitation\', documentation at \'/api/v1.0/precipitation/doc\'","Stations: \'/api/v1.0/stations\', documentation at \'/api/v1.0/stations/doc\'","Temperature Observations: \'/api/v1.0/tobs\', documentation at \'/api/v1.0/tobs/doc\'","Date range: \'/api/v1.0/<start>\' or \'/api/v1.0/<start>/<end>\', documentation at \'/api/v1.0/date_range/doc\'"]
    return render_template('index.html',title=title,paragraphs=paragraphs,list_items=list_items)

@app.route('/api/v1.0/precipitation')
def precipitation():
    d = {}
    results = db.session.query(Measurement).all()
    for result in results:
        key = result.date
        value = result.prcp
        if value:
            value = float(value)
        else:
            value = 0
        if key not in d:
            d[key] = value
        else:
            d[key] = d[key]+ value
    return jsonify(d)

@app.route('/api/v1.0/precipitation/doc')
def precipitation_doc():
    title="Precipitation"
    url='/api/v1.0/precipitation'
    ret="the precipitation as the value and the date as the key"
    return render_template('doc.html',title=title,url=url,ret=ret)

@app.route('/api/v1.0/stations')
def stations():
    l = []
    results = db.session.query(Station).all()
    for result in results:
        d = {'id':result.id, 'station':result.station, 'name':result.name, 'latitude':result.latitude, 'longitude':result.longitude, 'longitude':result.longitude}
        l.append(d)
    return jsonify(l)

@app.route('/api/v1.0/stations/doc')
def stations_doc():
    title="Stations"
    url='/api/v1.0/stations'
    ret="the list of stations"
    return render_template('doc.html',title=title,url=url,ret=ret)

@app.route('/api/v1.0/tobs')
def tobs():
    results = db.session.query(Measurement.station, func.count(Measurement.station)).filter(Measurement.prcp.is_not(None)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    station = results[0]
    max_date = db.session.query(func.max(Measurement.date)).one()
    max_date = max_date[0]
    timedelta = dt.timedelta(days=365)
    query_date=(dt.datetime.strptime(max_date, "%Y-%m-%d")-timedelta).date()
    results = db.session.query(Measurement.date,Measurement.tobs).filter(Measurement.date > query_date, Measurement.station == station).all()
    l = []
    for result in results:
        d= {'date':result.date,'tobs':result.tobs}
        l.append(d)
    data = {'station':station,'data':l}
    return jsonify(data)

@app.route('/api/v1.0/tobs/doc')
def tobs_doc():
    title="Temperature Observations"
    url='/api/v1.0/tobs'
    ret = 'the last year of tempeature observations for the most active station on the dataset'
    return render_template('doc.html',title=title,url=url,ret=ret)

@app.route('/api/v1.0/date_range/doc')
def date_range_doc():
    title="Date Range"
    url='/api/v1.0/<start> or /api/v1.0/<start>/<end>'
    ret='the minimum temperature, average temperature and max temperuate for a given date range, given a start date or a start and end date.'
    examples = ['/api/v1.0/2017-08-22', '/api/v1.0/2016-08-23/2017-08-23']
    return render_template('date_range_doc.html',title=title,url=url,ret=ret,examples=examples)


@app.route('/api/v1.0/<start>')
def start_date(start):
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except:
        return 'Not a date. Format is YYYY-mm-dd'
    max_list = []
    min_list = []
    avg_list = []
    max_temps = db.session.query(Measurement.date,func.max(Measurement.tobs)).filter(Measurement.date > start).group_by(Measurement.date).all()
    for max_temp in max_temps:
        max_list.append({'date':max_temp[0],'tmax':max_temp[1]})
    min_temps = db.session.query(Measurement.date,func.min(Measurement.tobs)).filter(Measurement.date > start).group_by(Measurement.date).all()
    for min_temp in min_temps:
        min_list.append({'date':min_temp[0],'tmin':min_temp[1]})
    avg_temps = db.session.query(Measurement.date,func.avg(Measurement.tobs)).filter(Measurement.date > start).group_by(Measurement.date).all()
    for avg_temp in avg_temps:
        avg_list.append({'date':avg_temp[0],'tavg':avg_temp[1]})
    for i in range(len(max_list)):
        if max_list[i]['date'] == min_list[i]['date'] and max_list[i]['date'] == avg_list[i]['date']:
            max_list[i]['tmin'] = min_list[i]['tmin']
            max_list[i]['tavg'] = avg_list[i]['tavg']
        else:
            print("if this message is printing, there may be data errors")
    return jsonify(max_list)
    
@app.route('/api/v1.0/<start>/<end>')
def date_range(start,end):
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except:
        return 'Not a date. Format is YYYY-mm-dd'
    max_list = []
    min_list = []
    avg_list = []
    max_temps = db.session.query(Measurement.date,func.max(Measurement.tobs)).filter(Measurement.date > start, Measurement.date < end).group_by(Measurement.date).all()
    for max_temp in max_temps:
        max_list.append({'date':max_temp[0],'tmax':max_temp[1]})
    min_temps = db.session.query(Measurement.date,func.min(Measurement.tobs)).filter(Measurement.date > start, Measurement.date < end).group_by(Measurement.date).all()
    for min_temp in min_temps:
        min_list.append({'date':min_temp[0],'tmin':min_temp[1]})
    avg_temps = db.session.query(Measurement.date,func.avg(Measurement.tobs)).filter(Measurement.date > start, Measurement.date < end).group_by(Measurement.date).all()
    for avg_temp in avg_temps:
        avg_list.append({'date':avg_temp[0],'tavg':avg_temp[1]})
    for i in range(len(max_list)):
        if max_list[i]['date'] == min_list[i]['date'] and max_list[i]['date'] == avg_list[i]['date']:
            max_list[i]['tmin'] = min_list[i]['tmin']
            max_list[i]['tavg'] = avg_list[i]['tavg']
        else:
            print("if this message is printing, there may be data errors")
    return jsonify(max_list)


if __name__ == '__main__':
    app.run(debug=True)