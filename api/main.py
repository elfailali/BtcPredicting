from fastapi import FastAPI
import pickle
from pydantic import BaseModel
import numpy as np
import joblib 
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import requests
import datetime
from datetime import datetime, timedelta
import time

# model 
lasso_model = joblib.load('lasso_model.pkl')
lasso = joblib.load('lasso.pkl')
class PredictionRequest(BaseModel):
    day: int
    month: int
    yesterday_price: float
    forecast_days: int


def connexion():
    try:
        conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="btc"
)       
    except pymysql.Error as e:
        return {"error": f"Failed to connect to database: {str(e)}"} 
    if (conn.open):
        print("Connected")
    else:
        print("Not connected")
   
    # Insertion(conn,data)
    return conn
    
def Insertion(conn,data,cursor):
    

    # Define the data to be inserted
    

    # Define the SQL query to insert the data
    query = """
        INSERT INTO predictions (date, prediction)
        VALUES (%(date)s, %(prediction)s)
    """

    # Execute the query with the data dictionary as input
    cursor.execute(query, data)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and the database connection
 
def Real_Insertion(conn,data,cur):
   
    cur.execute("""
                CREATE TABLE IF NOT EXISTS Real_data (
                    id SERIAL PRIMARY KEY,
                   date VARCHAR(20) NOT NULL,
                    prediction FLOAT NOT NULL
                )
            """)  

    # Define the data to be inserted
    

    # Define the SQL query to insert the data
    query = """
        INSERT INTO Real_data (date, prediction)
        VALUES (%(date)s, %(prediction)s)
    """

    # Execute the query with the data dictionary as input
    cur.execute(query, data)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and the database connection

def All_rael_Insertion(conn,data,cur):
    
    cur.execute("""
                CREATE TABLE IF NOT EXISTS All_Real_data (
                    id SERIAL PRIMARY KEY,
                   date VARCHAR(20) NOT NULL,
                    Open FLOAT NOT NULL,
                    High FLOAT NOT NULL,
                    Low FLOAT NOT NULL,
                    Close FLOAT NOT NULL
                )
            """)
    query = """
        INSERT INTO all_Real_data (date, Open, High, Low, Close)
        VALUES (%(date)s, %(Open)s, %(High)s, %(Low)s, %(Close)s)
    """
    #VALUES (%(date)s, %(Open)s, %(High)s, %(Low)s, %(Close)s)
    # Execute the query with the data dictionary as input
    cur.execute(query,data)

    # Commit the changes to the database
    conn.commit()   
def All_predict_Insertion(conn,data,cur):
    
    cur.execute("""
                CREATE TABLE IF NOT EXISTS All_predict_data (
                    id SERIAL PRIMARY KEY,
                   date VARCHAR(20) NOT NULL,
                    Open FLOAT NOT NULL,
                    High FLOAT NOT NULL,
                    Low FLOAT NOT NULL,
                    Close FLOAT NOT NULL
                )
            """)
    query = """
        INSERT INTO all_predict_data (date, Open, High, Low, Close)
        VALUES (%(date)s, %(Open)s, %(High)s, %(Low)s, %(Close)s)
    """
    #VALUES (%(date)s, %(Open)s, %(High)s, %(Low)s, %(Close)s)
    # Execute the query with the data dictionary as input
    cur.execute(query,data)

    # Commit the changes to the database
    conn.commit() 

def predict(data: PredictionRequest):
    day = data.day
    month = data.month
    yesterday_price = data.yesterday_price
    forecast_days = data.forecast_days

    # Connect to the PostgreSQL database
    conn=connexion()
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    date VARCHAR(20) NOT NULL,
                    prediction FLOAT NOT NULL
                )
            """)
    # Create the table if it doesn't exist
    current_day = day
    current_month = month
    current_price = yesterday_price
    # Make a prediction using the current inputs
    prediction = lasso_model.predict([[current_day, current_month, current_price]])
    date=datetime(year=2023, month=current_month, day=current_day)
    formatted_date = str(date.strftime("%B %d, %Y"))
    predi= prediction[0]
    data = {
    'date': formatted_date,
    'prediction': predi
        }
    Insertion(conn,data,cur)
    
    # Close the database connection.
    cur.close()
    conn.close()


def get_predict():
    conn = connexion()
    cur = conn.cursor()

    # Execute a SELECT query to retrieve all rows from the 'predictions' table
    cur.execute("SELECT * FROM predictions")

    # Fetch all rows and print them
    rows = cur.fetchall()
    # cur.close()
    # conn.close()
    
    return rows

#     # Close the cursor and database connection

def predict_New(timestampe,open_lag, high_lag, low_lag,close_lag):
    prediction = lasso.predict([[open_lag, high_lag, low_lag,close_lag]])
    data = {
        'date': timestampe,
        'Open': prediction[0][0],
        'High': prediction[0][1],
        'Low': prediction[0][2],
        'Close': prediction[0][3]
                }
    return data


def generate_url(url, start_date,end_date):
    return url+start_date+"&end_date="+end_date+"&ohlc=true"
# Send GET request to the API
def generate_date(url, start_date,end_date):
    new_url=generate_url(url, start_date,end_date)
    response = requests.get(new_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # Save the data to a JSON file
        
    return data
def get_end_Time():
    Day_current_date = datetime.now().date()
    Day_formatted_date = Day_current_date.strftime("%Y-%m-%d")
    Hour_current_time = datetime.now().time()
    # Format the time as "HH:MM"
    Hour_formatted_time = Hour_current_time.strftime("%H:%M")
    end_Time=str(Day_formatted_date)+"T"+str(Hour_formatted_time)
    return end_Time
def get_start_Time(number_of_minute):
    current_datetime = datetime.now()
    # Calculate the datetime 10 minutes ago
    ten_minutes_ago = current_datetime - timedelta(minutes=number_of_minute)
    # Format the datetime as desired (including day, month, and year)
    Y_M_D = ten_minutes_ago.strftime("%Y-%m-%d")
    H_M = ten_minutes_ago.strftime("%H:%M")
    start_time=str(Y_M_D)+"T"+str(H_M)
    return start_time

if __name__ == '__main__':
    # import uvicorn
    # uvicorn.run(app, host='localhost', port=5000)
    # # python -m uvicorn main:app --reload
    # # connexion()
    
    url = "https://production.api.coindesk.com/v2/price/values/BTC?start_date="
    while True:
        current_datetime = datetime.now()
        # Add 1 minute to the current datetime
        next_minute_datetime = current_datetime + timedelta(minutes=1)
        # Convert the next minute datetime to a timestamp
        next_minute_timestamp = next_minute_datetime.timestamp()
        start_time=get_start_Time(1)
        end_time=get_end_Time()
        pred=generate_date(url,start_time,end_time)
        entries = pred['data']['entries']
        print('data 1 min a go geted')
        data = {
        'date': entries[0][0],
        'Open': entries[0][1],
        'High': entries[0][2],
        'Low': entries[0][3],
        'Close': entries[0][4]
        }
        conn=connexion()
        cur = conn.cursor()
        All_rael_Insertion(conn,data,cur)
        cur.close()
        conn.close()
        pred_data=predict_New(next_minute_timestamp,entries[0][1], entries[0][2], entries[0][3],entries[0][4])
        print(pred_data)
        conn=connexion()
        cur = conn.cursor()
        All_predict_Insertion(conn,pred_data,cur)
        cur.close()
        conn.close()
        time.sleep(60)
        
    
    
    