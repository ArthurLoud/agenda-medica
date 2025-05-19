CREATE DATABASE agenda_db;
USE agenda_db


CREATE TABLE medicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE consultas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paciente VARCHAR(255) NOT NULL,
    medico_id INT,
    data DATE,
    hora TIME,
    FOREIGN KEY (medico_id) REFERENCES medicos(id)
);
