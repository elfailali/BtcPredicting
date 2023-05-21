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
lasso_model = joblib.load('lasso_with_close.pkl')
lasso = joblib.load('lasso.pkl')


# api 
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
def Insertion(conn,data,cur):
    

    # Define the data to be inserted
    cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                   date VARCHAR(20) NOT NULL,
                    prediction FLOAT NOT NULL
                )
            """)  
    

    # Define the SQL query to insert the data
    query = """
        INSERT INTO predictions (date, prediction)
        VALUES (%(date)s, %(prediction)s)
    """

    # Execute the query with the data dictionary as input
    cur.execute(query, data)

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


@app.get("/get_predict")
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

def close_prediction(timestampe,close_lag):
    prediction = lasso_model.predict([[close_lag]])
    data = {
        'date': timestampe,
        'prediction': prediction[0]
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
    Day_current = datetime.now()
    Day_current_date = Day_current.date()
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
    url = "https://production.api.coindesk.com/v2/price/values/BTC?start_date="
    while True:
        start_time=get_start_Time(1)
        end_time=get_end_Time()
        pred=generate_date(url,start_time,end_time)
        entries = pred['data']['entries']
        print('data 1 min a go geted')
        data = {
        'date': entries[0][0],
        'prediction': entries[0][4]
        }
        next_minute_timestamp = entries[0][0]+60000
        conn=connexion()
        cur = conn.cursor()
        Real_Insertion(conn,data,cur)
        cur.close()
        conn.close()
        pred_data=close_prediction(next_minute_timestamp,entries[0][4])
        print(pred_data)
        conn=connexion()
        cur = conn.cursor()
        Insertion(conn,pred_data,cur)
        cur.close()
        conn.close()
        time.sleep(60)
        
    
    
    