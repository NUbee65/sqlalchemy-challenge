#!/usr/bin/env python
# coding: utf-8

# In[ ]:

# Ignore SQLITE warnings related to Decimal numbers in the Chinook database
import warnings
warnings.filterwarnings('ignore')

#%%

#Import dependencies - dataframe, computation, storage, et.al.
import numpy as np
import pandas as pd
import re
import csv

#%%

#Import dependencies - date values and formats
import datetime as dt
from datetime import datetime
from datetime import date
from datetime import timedelta
import calendar

#%%

# Import dependencies - SQLalchemy
import sqlalchemy
from sqlalchemy import create_engine

#%%

# Import dependencies - browser exposure, API formatting
import json
import flask
from flask import Flask, jsonify, render_template
from app import app

# In[26]:

# Create an engine for the hawii.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


#%%

app = Flask(__name__)

#%% In[ ]:

@app.route('/')
def home():
    # We are about to learn how to render HTML pages in flask
    # return render_template(home.html)
    home = '\
        Welcome! You have reached a site dedicated (for the moment) to \n\
        Hawaiian Precipitation and Temperature data.  We hope you \n\
        will take time to splunk the site.  We even have a page that \n\
        may help you plan your next trip if Hawaii is the destination.\n\
        \n\
        Here is a list of available routes\n\
        \n\
        /api/v1.0/precipitation\n\
        /api/v1.0/stations\n\
        /api/v1.0/tobs\n\
        /api/v1.0/lookback/<start_date>\n\
        /api/v1.0/lookback/<start_date>/<end_date>"\n\
        /api/v1.0/vacation_planner//<vaca_start_date>/<vaca_end_date>'
    
    return(main)

urLlist = ["/",
           "/api/v1.0/precipitation",
           "/api/v1.0/stations",
           "/api/v1.0/tobs",
           "/api/v1.0/lookback/<start_date>",
           "/api/v1.0/lookback/<start_date>/<end_date>",
           "/api/v1.0/vacation_planner//<vaca_start_date>/<vaca_end_date>"]

#%%

# Return daily precipitation averaged across all stations for the LTM period

@app.route('/api/v1.0/precipitation')
def precip():
    conn = engine.connect()

    query = '''
            SELECT
                date,
                AVG(prcp) AS avg_prcp
            FROM
                measurement
            WHERE
                date > (SELECT date(MAX(date),'-1 year') FROM measurement)
            GROUP BY
                date
            ORDER BY
                date ASC
            '''
    
    prcp_ltm_df = pd.read_sql(query, conn)
    prcp_ltm_df['date'] = pd.to_datetime(prcp_ltm_df['date'])
    prcp_ltm_df = prcp_ltm_df.sort_values('date')
    prcp_ltm_json = prcp_ltm_df.to_json(orient='records', date_format='iso')

    conn.close()
    
    return prcp_ltm_json

#%% In[47]:

# Return list of stations

@app.route('/api/v1.0/stations')
def stations():
    conn = engine.connect()
    query = "SELECT  DISTINCT name FROM station"
    
    station_names_df =  pd.read_sql(query, conn)
    station_names = station_names_df["name"].tolist()
    
    stations_list = []
    for name in station_names:
        name1 = name.title()
        name2 = name1.replace(" ", "")
        name3 = re.search(r"[a-zA-Z]*", name2).group()
        name4 = re.sub(r"(?<=\w)([A-Z])", r" \1", name3)
        stations_list.append(name4)
    
    stations_json = json.dumps(stations_list)
    
    conn.close()
    
    return stations_json

#%%

# Return station records for most active station in LTM period

@app.route('/api/v1.0/tobs')
def no1_station_ltm():
    conn = engine.connect()
    
    query = f'''
            SELECT
                s.station,
                s.name,
                COUNT(*) AS temp_obs
            FROM
                measurement m
                INNER JOIN station s
                ON m.station = s.station
            WHERE
                m.tobs IS NOT NULL
                AND m.date > (SELECT date(MAX(date),'-1 year') FROM measurement)
            GROUP BY
                m.station,
                s.name
            ORDER BY
                temp_obs DESC
            '''
    stations_tobs_activity_level_ltm_df =  pd.read_sql(query, conn)
    most_active_station_ltm = stations_tobs_activity_level_ltm_df.values[0,1]
    most_active_station_ltm_id = stations_tobs_activity_level_ltm_df.values[0,0]
        
    query2 = f'''
            SELECT date, m.tobs, s.name
            FROM 
                measurement m
                JOIN station s
                ON m.station = s.station
            WHERE
                m.station = '{most_active_station_ltm_id}'
                AND m.date > (SELECT date(MAX(date),'-1 year') FROM measurement)
            ORDER BY
                m.date ASC
            '''
    no1_active_tobs_station_ltm_df =  pd.read_sql(query2, conn)
    no1_active_tobs_station_ltm_json = no1_active_tobs_station_ltm_df.to_json(orient='records',date_format='iso')

    conn.close()
    
    return no1_active_tobs_station_ltm_json

#%%

@app.route('/api/v1.0/lookback/<start_date>')
def calc_2_temps_better_method(start_date):
    conn = engine.connect()
   
    query = f'''
            SELECT
                MIN(dmin) as min_t,
                MAX(dmax) as max_t,
                AVG(davg) as wavg_t
            FROM 
                (SELECT
                    MIN(m.tobs) AS dmin,
                    MAX(m.tobs) AS dmax,
                    AVG(m.tobs) AS davg
                FROM
                    measurement m
                WHERE
                    m.date >= '{start_date}'
                GROUP BY
                    m.date
                ORDER BY
                    m.date
                ) AS P;
            '''
    temps_2_better_method_df = pd.read_sql(query, conn)
    temps_2_better_method_json = temps_2_better_method_df.to_json(orient='records', date_format='iso')
    
    conn.close()
    
    return temps_2_better_method_json


#%%

@app.route('/api/v1.0/lookback/<start_date>/<end_date>')
def calc_temps(start_date, end_date):
    conn = engine.connect()
    
    query = f'''
            SELECT
                MIN(dmin) as min_t,
                MAX(dmax) as max_t,
                AVG(davg) as wavg_t
            FROM 
                (SELECT
                    MIN(m.tobs) AS dmin,
                    MAX(m.tobs) AS dmax,
                    AVG(m.tobs) AS davg
                FROM
                    measurement m
                WHERE
                    m.date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY
                    m.date
                ORDER BY
                    m.date
                ) AS P;
            '''
    temps_better_method_df = pd.read_sql(query, conn)
    temps_better_method_json = temps_better_method_df.to_json(orient='records', date_format='iso')
    
    conn.close()
    
    return temps_better_method_json

#%%

@app.route('/api/v1.0/vacation_planner/<vaca_start_date>/<vaca_end_date>')

def vaca_calc_temp(vaca_start_date, vaca_end_date):
    conn = engine.connect()    
    
    vacation_dates_x = []
    vacation_dates = [vaca_start_date,vaca_end_date]
    for date_x in vacation_dates:
        vals_x = date_x.split("-")
        vacation_date_x = '2021' + "-" + vals_x[1] + "-" + vals_x[2]
        vacation_dates_x.append(vacation_date_x)
    
    query = f'''
            SELECT 
                MIN(dmin) as min_t,
                MAX(dmax) as max_t,
                AVG(davg) as wavg_t
            FROM 
                (SELECT
                    MIN(m.tobs) AS dmin,
                    MAX(m.tobs) AS dmax,
                    AVG(m.tobs) AS davg
                    
                 FROM
                    measurement m
                 WHERE
                    m.date BETWEEN -- 2010
                        (SELECT date('{vacation_dates_x[0]}','-11 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-11 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2011
                        (SELECT date('{vacation_dates_x[0]}','-10 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-10 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2012
                        (SELECT date('{vacation_dates_x[0]}','-9 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-9 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2013
                        (SELECT date('{vacation_dates_x[0]}','-8 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-8 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2014
                        (SELECT date('{vacation_dates_x[0]}','-7 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-7 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2015
                        (SELECT date('{vacation_dates_x[0]}','-6 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-6 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2016
                        (SELECT date('{vacation_dates_x[0]}','-5 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-5 year') FROM measurement)
        
                    OR m.date BETWEEN -- 2017
                        (SELECT date('{vacation_dates_x[0]}','-4 year') FROM measurement) 
                        AND (SELECT date('{vacation_dates_x[1]}','-4 year') FROM measurement)
        
                 GROUP BY
                    m.date
                 ORDER BY
                    m.date
                ) AS P;
                '''
    
    vaca_temp_df = pd.read_sql(query, conn)
    vaca_temp_json = vaca_temp_df.to_json(orient='records', date_format='iso')
    
    conn.close()
    
    return vaca_temp_json


#%% In[49]:

if __name__ == '__main__':
    app.run(debug=True)














