CREATE DATABASE IF NOT EXISTS phonebook;
USE phonebook;


CREATE TABLE IF NOT EXISTS users (
	userid INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
	cate_id INT PRIMARY KEY AUTO_INCREMENT,
    cate_name VARCHAR(255) NOT NULL,
    userid INT,
    FOREIGN KEY (userid) REFERENCES users(userid)
);

CREATE TABLE IF NOT EXISTS contacts (
	contact_id INT PRIMARY KEY AUTO_INCREMENT,
    contact_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255),
    address VARCHAR(255),
    userid INT,
    cate_id INT,
    FOREIGN KEY (userid) REFERENCES users(userid),
    FOREIGN KEY (cate_id) REFERENCES categories(cate_id)
);