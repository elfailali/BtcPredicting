from fastapi import FastAPI
import pickle
from pydantic import BaseModel
import numpy as np
import joblib 
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

# model_lasso
lasso_model = joblib.load('lasso_model.pkl')
class PredictionRequest(BaseModel):
    day: int
    month: int
    yesterday_price: float
    forecast_days: int



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
        conn = psycopg2.connect(
            host="localhost",
            port = "5432",
            database="postgres",
            user="postgres",
            password="4242"
        )
    except psycopg2.Error as e:
        return {"error": f"Failed to connect to database: {str(e)}"}
    return conn


@app.post("/predict")
def predict(data: PredictionRequest):
    day = data.day
    month = data.month
    yesterday_price = data.yesterday_price
    forecast_days = data.forecast_days

    # Connect to the PostgreSQL database
    conn=connexion()

    # Create the table if it doesn't exist
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    prediction FLOAT NOT NULL
                )
            """)

    predictions = []
    current_day = day
    current_month = month
    current_price = yesterday_price

    for _ in range(forecast_days):
        # Make a prediction using the current inputs
        prediction = lasso_model.predict([[current_day, current_month, current_price]])
        predictions.append({"date": datetime(year=2023, month=current_month, day=current_day).strftime("%d/%m/%Y"), "prediction": prediction[0]})

        # Insert the prediction into the PostgreSQL database
        with conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO postgres (date, prediction) VALUES (%s, %s)
                    """, (datetime(year=2023, month=current_month, day=current_day), prediction[0]))
                except psycopg2.Error as e:
                    return {"error": f"Failed to insert data into database: {str(e)}"}
                

        # Update the inputs 
        current_date = datetime(year=2023, month=current_month, day=current_day)
        next_date = current_date + timedelta(days=1)
        current_day = next_date.day
        current_month = next_date.month
        current_price = prediction[0]

    # Close the database connection
    conn.close()

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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=5000)
    # python -m uvicorn main:app --reload
    
    