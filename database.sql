-- ============================================
-- COURSE PLATFORM DATABASE
-- ============================================

CREATE DATABASE IF NOT EXISTS course_platform;

USE course_platform;


-- ============================================
-- USERS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- COURSES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    instructor VARCHAR(150) NOT NULL,
    image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    course_title VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);


-- ============================================
-- ADMIN ACCOUNT
-- ============================================

INSERT IGNORE INTO users
(name, email, password, role)
VALUES
('Admin', 'admin@course.com', 'Admin@123', 'admin');


-- ============================================
-- SAMPLE COURSES
-- ============================================

INSERT INTO courses
(title, description, price, instructor, image)
VALUES

(
    'Full Stack Web Development',
    'Learn HTML, CSS, JavaScript, Node.js, React and databases.',
    4999.00,
    'Imran',
    NULL
),

(
    'Cyber Security Fundamentals',
    'Learn cybersecurity concepts, threats, vulnerabilities and defense.',
    3999.00,
    'Rahul',
    NULL
),

(
    'Python Programming',
    'Learn Python from beginner level to advanced programming.',
    2999.00,
    'Arjun',
    NULL
),

(
    'AWS Cloud Computing',
    'Learn AWS services, EC2, S3, IAM, VPC and cloud fundamentals.',
    5999.00,
    'Ahmed',
    NULL
),

(
    'React.js Development',
    'Build modern and responsive web applications using React.',
    3499.00,
    'Vikram',
    NULL
),

(
    'JavaScript Masterclass',
    'Master JavaScript, DOM, APIs, async programming and ES6.',
    2499.00,
    'Sameer',
    NULL
),

(
    'Ethical Hacking',
    'Learn ethical hacking concepts, reconnaissance and security testing.',
    4499.00,
    'Imran',
    NULL
),

(
    'SQL and Database Management',
    'Learn SQL, MySQL, database design, queries and database management.',
    1999.00,
    'Kiran',
    NULL
),

(
    'Linux Administration',
    'Learn Linux commands, users, permissions, services and administration.',
    2499.00,
    'Mohammed',
    NULL
),

(
    'Web Application Security',
    'Learn OWASP concepts, web vulnerabilities and secure coding.',
    4999.00,
    'Imran',
    NULL
),

(
    'Networking and CCNA',
    'Learn networking fundamentals, routing, switching and CCNA concepts.',
    3499.00,
    'Naveen',
    NULL
),

(
    'AI and Machine Learning',
    'Learn AI fundamentals, Python, machine learning and data concepts.',
    6999.00,
    'Priya',
    NULL
);


-- ============================================
-- VERIFY DATABASE
-- ============================================

USE course_platform;

SHOW TABLES;

SELECT * FROM users;

SELECT * FROM courses;