from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="MyNewPass123!",
        database="course_platform"
    )


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def files(filename):
    file_path = os.path.join(BASE_DIR, filename)

    if os.path.isfile(file_path):
        return send_from_directory(BASE_DIR, filename)

    return "File not found", 404


@app.route("/register", methods=["POST"])
def register():

    db = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No registration data received."
            })

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({
                "success": False,
                "message": "Please fill all fields."
            })

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, password, "student")
        )

        db.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful!"
        })

    except mysql.connector.IntegrityError:
        return jsonify({
            "success": False,
            "message": "Email already registered."
        })

    except Exception as error:
        print("REGISTER ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Registration error: " + str(error)
        })

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@app.route("/login", methods=["POST"])
def login():

    db = None
    cursor = None

    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Please enter email and password."
            })

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            WHERE email = %s
            AND password = %s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            })

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": user
        })

    except Exception as error:
        print("LOGIN ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Login error: " + str(error)
        })

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@app.route("/api/courses", methods=["GET"])
def get_courses():

    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, title, description, price,
                   instructor, image, created_at
            FROM courses
            ORDER BY id DESC
            """
        )

        courses = cursor.fetchall()

        return jsonify({
            "success": True,
            "courses": courses
        })

    except Exception as error:
        print("COURSES ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not load courses."
        })

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@app.route("/api/orders", methods=["POST"])
def create_order():
    db = None
    cursor = None

    try:
        data = request.get_json() or {}
        required_fields = [
            "user_id", "full_name", "phone", "address", "city",
            "state", "postal_code", "country", "payment_method", "items"
        ]
        if any(not data.get(field) for field in required_fields) or not data["items"]:
            return jsonify({"success": False, "message": "Please complete all checkout fields."}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_number VARCHAR(40) NOT NULL UNIQUE,
                user_id INT NOT NULL,
                full_name VARCHAR(120) NOT NULL,
                phone VARCHAR(30) NOT NULL,
                address VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                postal_code VARCHAR(20) NOT NULL,
                country VARCHAR(100) NOT NULL,
                payment_method VARCHAR(40) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'placed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                course_title VARCHAR(200) NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
        """)
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'payment_method'")
        if not cursor.fetchone():
            cursor.execute(
                "ALTER TABLE orders ADD COLUMN payment_method VARCHAR(40) NOT NULL DEFAULT 'Cash on Delivery'"
            )

        items = data["items"]
        total = sum(float(item.get("price", 0)) for item in items)
        order_number = "CP-" + uuid.uuid4().hex[:10].upper()
        cursor.execute("""
            INSERT INTO orders
            (order_number, user_id, full_name, phone, address, city, state,
             postal_code, country, payment_method, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_number, data["user_id"], data["full_name"], data["phone"],
            data["address"], data["city"], data["state"], data["postal_code"],
            data["country"], data["payment_method"], total
        ))
        order_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO order_items (order_id, course_title, price) VALUES (%s, %s, %s)",
            [(order_id, item.get("title", "Course"), float(item.get("price", 0))) for item in items]
        )
        db.commit()
        return jsonify({
            "success": True,
            "message": "Order placed successfully.",
            "order_number": order_number
        })
    except Exception as error:
        if db:
            db.rollback()
        print("ORDER ERROR:", error)
        return jsonify({"success": False, "message": "Could not place your order."}), 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@app.route("/api/admin/courses", methods=["POST"])
def upload_course():

    db = None
    cursor = None

    try:
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        instructor = request.form.get("instructor")

        image = request.files.get("image")

        if not title or not description or not price or not instructor:
            return jsonify({
                "success": False,
                "message": "Please fill all course fields."
            })

        image_path = None

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )

            image_path = "/uploads/" + filename

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO courses
            (title, description, price, instructor, image)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                title,
                description,
                price,
                instructor,
                image_path
            )
        )

        db.commit()

        return jsonify({
            "success": True,
            "message": "Course uploaded successfully!"
        })

    except Exception as error:
        print("UPLOAD ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not upload course."
        })

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@app.route("/uploads/<path:filename>")
def uploaded_image(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


if __name__ == "__main__":

    print("================================")
    print("COURSE PLATFORM SERVER")
    print("================================")
    print("Open: http://localhost:3000")

    app.run(
        host="0.0.0.0",
        port=3000,
        debug=True
    )
    