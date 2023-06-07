# Import the dependencies.

################################################

from flask import Flask, jsonify

import datetime as dt 
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database Setup

engine = create_engine(f"sqlite:///Resources/hawaii.sqlite") 

#################################################

# reflect an existing database into a new model

Base = automap_base()
Base.prepare(autoload_with=engine)

# assign class references

measurement = Base.classes.measurement 
station = Base.classes.station
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    # Get all the routes
    routes = []
    for rule in app.url_map.iter_rules():
        # check if is a parametized route to append as a string reference as it doesnt show parameters <>
        if rule.rule == "/api/v1.0/<year>/<month>/<day>":
                routes.append("/api/v1.0/year/month/day")
                continue   
        # check if is a parametized route to append as a string reference as it doesnt show parameters <>
        if rule.rule == "/api/v1.0/<syear>/<smonth>/<sday>/<eyear>/<emonth>/<eday>":
                routes.append("/api/v1.0/year/month/day/year/month/day")
                continue      
        # check if route endpoint doesnt not contain static data to append
        if rule.endpoint != 'static':
            print(rule.rule)
            routes.append(rule.rule)
    
    # Return the list of routes
    return "<br>".join(routes)

@app.route("/api/v1.0/precipitation")
def date_precipitation_last_year():
        # Create a query that collects only the date and precipitation for the last year of data without passing the date as variable
       
        # non-hardcoded query to obtain max date 
        #data_from_one_year_before = session.query(measurement.date,measurement.prcp).where(measurement.c.date >= (dt.datetime.strptime(session.query(func.max(measurement.date)).scalar(),"%Y-%m-%d") - dt.timedelta(days=365)).date()).all()
        
        # hardcoded date
        year = dt.date(2017,8,23) - dt.timedelta(days=365)

        # query with hardcoded date
        result = session.query(measurement.date, measurement.prcp).filter(measurement.date>=year).all()
        session.close()

        # assign the key and values to store in dict from result query
        date_prcp_dict = {date: prcp for date, prcp in result}

        # optional print dict
        print(date_prcp_dict)

        return jsonify(date_prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
       # get all stations

       stations_data  = session.query(station.station).all()

       # close session
       session.close()

       # optional print stations_data
       print(stations_data)

       # convert stations_data into list making into one dimension list using np
       stations_data=list(np.ravel(stations_data))

       # optional print stations data list
       print(stations_data)

       return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def get_previous_12months_data():
        #Design a query to get the previous 12 months of temperature observation (TOBS) data that filters by the station that has the greatest number of observations
      
        """
        # get the date twelve months before from most active station (non-hard-coded)
        date_twelve_months_before_station_most_tobs = (dt.datetime.strptime(session.query(func.max(measurement.date).filter(measurement.station == "USC00519281")).scalar(),"%Y-%m-%d") - dt.timedelta(days=365)).date()
        print(date_twelve_months_before_station_most_tobs)
        #get the data from most active station based on dates that are greater or equal than the queried date before (hard-coded station) & (non-hard-coded date)
        filtered_data = session.query(measurement.c.date,measurement.c.tobs).filter(measurement.c.station == "USC00519281",measurement.c.date>=date_twelve_months_before_station_most_tobs).all()
        """

        # optional check which is the max date based on station with most tobs  on query
        print(session.query(func.max(measurement.date).filter(measurement.station == "USC00519281")).scalar())
        
        # hard-coded date substract with twelve months to obtain start-date
        year = dt.date(2017,8,18)-dt.timedelta(days=365)

        # query the data from the most active station based on the hardcoded start-date & hard-coded most active station
        result = session.query(measurement.date,measurement.tobs).filter(measurement.date>=year,measurement.station=="USC00519281").all()
        
        # close session
        session.close()
        
        # create JSON object of tobs data
        result = [dict(date=date,tobs=tobs) for date,tobs in result]
        return jsonify(result)

@app.route("/api/v1.0/<year>/<month>/<day>")
def min_max_average_temperature(year,month,day):
        #check if date is valid
        try:
               int(year)
               int(month)
               int(day)
        except ValueError:
               return "Only numbers are accepted"

        # check if date is valid format incluiding testing from(length,days corresponding to months,valid dates, valid months, valid years etc...)
        try:
               date_str = f"{year}-{month}-{day}"
               # Parse the string to date
               start_date = dt.datetime.strptime(date_str,"%Y-%m-%d").date()
        except:
                return "Date format is invalid"
        
        # get min,max and avg based on start date
        min_max_avg_based_on_start_date = session.query(func.min(measurement.tobs).label("Min temp"),func.max(measurement.tobs).label("Max temp"),func.avg(measurement.tobs).label("Average temperature")).filter(measurement.date >=start_date).all()
        
        # (optional) verify that returned data is based on the start date
        data = session.query(measurement.date,measurement.tobs).filter(measurement.date >= start_date).all()
        #print(data)

        # close session
        session.close()

        # convert to one dimension list the returned min,max and avg
        min_max_avg_based_on_start_date = list(np.ravel(min_max_avg_based_on_start_date))

        return jsonify(dict(min_temperature=min_max_avg_based_on_start_date[0],max_temperature=min_max_avg_based_on_start_date[1],avg_temperature=min_max_avg_based_on_start_date[2]))


@app.route("/api/v1.0/<syear>/<smonth>/<sday>/<eyear>/<emonth>/<eday>")
def min_max_average_temperature_intervals(syear,smonth,sday,eyear,emonth,eday):
        #check if dates are  valid
        try:
               int(syear)
               int(smonth)
               int(sday)
               int(eyear)
               int(emonth)
               int(eday)

        except ValueError:
               return "Not numbers"
        
        # check if date is valid format incluiding testing from(length,days corresponding to months,valid dates, valid months, valid years etc...)
        try:
               start_date_str = f"{syear}-{smonth}-{sday}"
               end_date_str = f"{eyear}-{emonth}-{eday}"

               # Parse the strings  and convert to dates
               start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
               end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d").date()

        except:
                return "not valid dates"
        
        #check that end date is greater than start date
        if(start_date>end_date):
               return "start date cannot be greather than  end date"
        
        # get min,max and avg based on range start-date and end-date
        min_max_avg_based_on_start_date_and_end_date = session.query(func.min(measurement.tobs).label("Min temp"),func.max(measurement.tobs).label("Max temp"),func.avg(measurement.tobs).label("Average temperature")).filter(measurement.date >= start_date,measurement.date <= end_date).all()
        
        # (optional) query the data from start and end dates to verify 
        data = session.query(measurement.date,measurement.tobs).filter(measurement.date >= start_date,measurement.date <= end_date).all()
        print(data)

        # close session
        session.close()
        
        # convert the min,max,avg into one dimension list
        min_max_avg_based_on_start_date_and_end_date = list(np.ravel(min_max_avg_based_on_start_date_and_end_date))

        return jsonify(dict(min_temperature=min_max_avg_based_on_start_date_and_end_date[0],max_temperature=min_max_avg_based_on_start_date_and_end_date[1],avg_temperature=min_max_avg_based_on_start_date_and_end_date[2]))


if __name__=="__main__":
        app.run(debug=True)




