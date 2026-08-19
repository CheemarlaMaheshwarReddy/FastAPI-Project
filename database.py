import psycopg2
connection = psycopg2.connect(
    host="localhost",
    port=5433,
    database="fastapi_db",
    user="fastapi_user",
    password="FastAPI123"
)
print("Database connection was successful!")

cursor = connection.cursor()
cursor.execute ( "SELECT current_database();")
row = cursor.fetchone()
print(row)
