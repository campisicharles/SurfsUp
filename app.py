import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True) 

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    print("Server received request for 'Rain' page...")
    query_date = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).filter(Measurement.date).all()

    rainamount = []
    for date, prcp in precip:
        rain_dict = {}
        rain_dict["date"] = date
        rain_dict["prcp"] = prcp
        rainamount.append(rain_dict)

    return jsonify(rainamount)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    print("Server received request for 'Station' page...")
    activestation = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    stationlist = list(np.ravel(activestation))
    return jsonify(stationlist)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    """HAD SOME SYNTAX ERRORS IN HERE - had prcp instead of tobs - damn cut and paste from the above and forgot to switch"""
    print("Server received request for 'Observation' page...")
    query_date = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    raintrack = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.date).all()
    observationlist = list(np.ravel(raintrack))
 
    return jsonify(observationlist)


# Saw a bunch of different ways to do these, tried a couple, but I can't seem to get either one to display
# spent a lot of time trying to get these to work - no dice

@app.route('/api/v1.0/<start>')
def start(start):
    startdate = dt.datetime(2012, 2, 28)
    startdata = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= startdate).all()    
    
    temps = []
    for result in startdata:
        data_dict = {}
        data_dict["date"] = result[0]
        data_dict["mintemp"] = result[1]
        data_dict["avgtemp"] = result[2]
        data_dict["maxtemp"] = result[3]
        temps.append(data_dict)
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    startdate = dt.datetime(2012, 2, 28)
    query_date = dt.datetime(2012, 2, 28) - dt.timedelta(days=7)
    startend = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= startdate).filter(Measurement.date <= query_date).all()
    tripstartend = list(np.ravel(startend))
    
    return jsonify(tripstartend)

if __name__ == "__main__":
    app.run(debug=True)