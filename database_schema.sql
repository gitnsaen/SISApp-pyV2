CREATE DATABASE IF NOT EXISTS sis_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sis_db;

CREATE TABLE IF NOT EXISTS colleges (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS programs (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    college_code VARCHAR(10) DEFAULT NULL,
    FOREIGN KEY (college_code) REFERENCES colleges(code) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(9) PRIMARY KEY,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    program_code VARCHAR(10) DEFAULT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    gender ENUM('Male', 'Female') NOT NULL,
    FOREIGN KEY (program_code) REFERENCES programs(code) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_students_lastname ON students(lastname);
CREATE INDEX idx_students_program ON students(program_code);
CREATE INDEX idx_programs_college ON programs(college_code);