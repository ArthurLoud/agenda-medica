import mysql.connector
from mysql.connector import Error

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="agenda_db"
    )

def agendar_consulta(paciente, medico_id, data, hora):
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Verifica se já existe uma consulta no mesmo horário (qualquer paciente, qualquer médico)
        cursor.execute("""
            SELECT * FROM consultas 
            WHERE data = %s AND hora = %s
        """, (data, hora))

        if cursor.fetchone():
            return False  # Já existe consulta nesse horário (para qualquer paciente)

        # Insere a nova consulta
        cursor.execute("""
            INSERT INTO consultas (paciente, medico_id, data, hora)
            VALUES (%s, %s, %s, %s)
        """, (paciente, medico_id, data, hora))

        conn.commit()
        return True

    except Error as e:
        print("Erro ao agendar consulta:", e)
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def listar_consultas():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT c.id, c.paciente, m.nome AS medico, c.data, c.hora
            FROM consultas c
            JOIN medicos m ON c.medico_id = m.id
            ORDER BY c.data, c.hora
        """)
        return cursor.fetchall()

    except Error as e:
        print("Erro ao listar consultas:", e)
        return []

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def deletar_consulta(consulta_id):
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM consultas WHERE id = %s", (consulta_id,))
        conn.commit()

        return cursor.rowcount > 0  # True se deletou

    except Error as e:
        print("Erro ao deletar consulta:", e)
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def criar_tabelas():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                paciente VARCHAR(100) NOT NULL,
                medico_id INT,
                data DATE,
                hora TIME,
                FOREIGN KEY (medico_id) REFERENCES medicos(id)
            )
        """)

        conn.commit()
    except Error as e:
        print("Erro ao criar tabelas:", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
