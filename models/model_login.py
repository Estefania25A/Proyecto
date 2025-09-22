# models/model_login.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from conexion.conexion import conexion, cerrar_conexion
from mysql.connector import Error

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        # Flask-Login usa .id como string
        self.id = str(id_usuario)
        self.user_id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password_hash = password  # valor almacenado en la columna password

    def verificar_password(self, password_plano: str) -> bool:
        """Verifica contraseña en texto plano contra el hash guardado."""
        try:
            return check_password_hash(self.password_hash, password_plano)
        except Exception:
            return False

    @staticmethod
    def obtener_por_id(user_id: int):
        conn = conexion()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT id_usuario, nombre, email, password FROM usuarios WHERE id_usuario = %s",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                return Usuario(row['id_usuario'], row['nombre'], row['email'], row['password'])
            return None
        except Error as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None
        finally:
            try:
                cur.close()
            except Exception:
                pass
            cerrar_conexion(conn)

    @staticmethod
    def obtener_por_mail(email: str):
        conn = conexion()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT id_usuario, nombre, email, password FROM usuarios WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
            if row:
                return Usuario(row['id_usuario'], row['nombre'], row['email'], row['password'])
            return None
        except Error as e:
            print(f"Error al obtener usuario por email: {e}")
            return None
        finally:
            try:
                cur.close()
            except Exception:
                pass
            cerrar_conexion(conn)

    @staticmethod
    def crear_usuario(email: str, password_plano: str, nombre: str):
        """Crea un usuario y devuelve la instancia creada (hash usando PBKDF2)."""
        conn = conexion()
        cur = conn.cursor()
        cur2 = None
        try:
            password_hash = generate_password_hash(
                password_plano,
                method='pbkdf2:sha256:600000',
                salt_length=16
            )
            cur.execute(
                "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                (nombre, email, password_hash)
            )
            conn.commit()

            # Recuperar el usuario recién creado
            cur2 = conn.cursor(dictionary=True)
            cur2.execute(
                "SELECT id_usuario, nombre, email, password FROM usuarios WHERE email = %s",
                (email,)
            )
            row = cur2.fetchone()
            if row:
                return Usuario(row['id_usuario'], row['nombre'], row['email'], row['password'])
            return None
        except Error as e:
            print(f"Error al crear usuario: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            return None
        finally:
            try:
                if cur2:
                    cur2.close()
            except Exception:
                pass
            try:
                cur.close()
            except Exception:
                pass
            cerrar_conexion(conn)
