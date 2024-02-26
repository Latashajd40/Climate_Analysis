# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import json
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)


# Assign the measurement class to a variable called `Measurement` and
Measurement = Base.classes.measurement

# the station class to a variable called `Station`
Station = Base.classes.station


# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################

#create an app
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

#define static route
@app.route("/")
def home():
    """List all available routes"""
    return(
        f"Available routes: </br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end></br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve the last 12 months of data to a dictionary using date as the key and prcp as the value"""
    #create a link from Python to the database
    session = Session(engine)
    
    #query the data
    query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= "2016-08-23").all()
    
    session.close()
    
    #create a dictionary from the query
    weather = []
    
    for date, prcp in query:
        precipitation_dict = {date: prcp}
        weather.append(precipitation_dict)

    return jsonify(weather)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    #create a link from Python to the database
    session = Session(engine)
    
    #query the data
    query = session.query(Measurement.station).\
    group_by(Measurement.station).all()
    
    query_list = [dict(row) for row in query]
    
    json_data = json.dumps(query_list)
    
    session.close()
    
    return(json_data)

@app.route("/api/v1.0/tobs")
def total_observations():
    """Query dates and temperature observations of the most active station for the previous year of data"""

    #create a link from Python to the database
    session = Session(engine)  
    
    previous_twelve = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == 'USC00519281').\
                filter(func.strftime("%Y-%m-%d", Measurement.date) >= "2016-08-23").\
                group_by(Measurement.date).order_by(Measurement.date).all()
                
    query_list = [dict(row) for row in previous_twelve]
    
    json_data = json.dumps(query_list)
    
    session.close()
    
    return(json_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    try:
        # Attempt to parse the date string
        datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "The start date entered is not in the correct format of 'YYYY-MM-DD'"}), 404
    
    # Create a link from Python to the database
    session = Session(engine)
    
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    station_summary = session.query(*sel).filter(Measurement.date >= start).all()
    
    session.close()
    
    query = []
    
    for min, max, avg in station_summary:
        new_dict = {}
        new_dict['Min'] = min
        new_dict['Max'] = max
        new_dict['Avg'] = avg
        query.append(new_dict)
    
    return jsonify(query)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end):
      
    try:
        # Attempt to parse the date string
        datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "The start date entered is not in the correct format of 'YYYY-MM-DD'"}), 404
    
    try:
        # Attempt to parse the date string
        datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "The end date entered is not in the correct format of 'YYYY-MM-DD'"}), 404
    
    # Create a link from Python to the database
    session = Session(engine)
    
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    station_summary = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end).all()
    
    session.close()
    
    query = []
    
    for min, max, avg in station_summary:
        new_dict = {}
        new_dict['Min'] = min
        new_dict['Max'] = max
        new_dict['Avg'] = avg
        query.append(new_dict)
    
    return jsonify(query)
    

if __name__ == '__main__':
    app.run(debug=True)
    
    