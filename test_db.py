import mysql.connector

print("Starting MySQL test...")

try:
    db = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="MyNewPass123!",
        database="course_platform"
    )

    print("MYSQL CONNECTION SUCCESSFUL!")

    db.close()

except Exception as e:
    print("MYSQL CONNECTION FAILED!")
    print("ERROR:", e)