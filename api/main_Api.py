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
@app.get("/get_all_predict")
def get_predict():
    conn = connexion()
    cur = conn.cursor()
    # Execute a SELECT query to retrieve all rows from the 'predictions' table
    cur.execute("SELECT * FROM all_predict_data")

    # Fetch all rows and print them
    rows = cur.fetchall()
    # cur.close()
    # conn.close()
    
    return rows   
@app.get("/get_all_real")
def get_predict():
    conn = connexion()
    cur = conn.cursor()

    # Execute a SELECT query to retrieve all rows from the 'predictions' table
    cur.execute("SELECT * FROM all_real_data")

    # Fetch all rows and print them
    rows = cur.fetchall()
    # cur.close()
    # conn.close()
    
    return rows
@app.get("/get_close_real")
def get_predict():
    conn = connexion()
    cur = conn.cursor()

    # Execute a SELECT query to retrieve all rows from the 'predictions' table
    cur.execute("SELECT * FROM real_data")

    # Fetch all rows and print them
    rows = cur.fetchall()
    # cur.close()
    # conn.close()
    
    return rows
@app.get("/get_close_predict")
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
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=5000)
    