import psycopg2
connection = psycopg2.connect(
    host="localhost",
    database="fastapi",
    user="postgres",
    password="YourNewPassword"
)
print("Database connection was successful!")

cursor = connection.cursor()
cursor.execute (
    "SELECT * FROM products"
)
row = cursor.fetchone()
print(row)