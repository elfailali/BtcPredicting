import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
     host="localhost",
    port = "5432",
    database="postgres",
    user="postgres",
    password="4242"
)

# Create a cursor object to execute queries
cur = conn.cursor()

# Execute a SELECT query to retrieve all rows from the 'predictions' table
cur.execute("SELECT * FROM postgres")

# Fetch all rows and print them
rows = cur.fetchall()
for row in rows:
    print(row)

# Close the cursor and database connection
cur.close()
conn.close()