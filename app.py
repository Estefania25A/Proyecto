from flask import Flask
from conexion.conexion import get_connection

app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return """
        <h1>Bienvenido a mi proyecto Flask</h1>
        <p>Puedes visitar:</p>
        <ul>
            <li><a href='/usuarios'>Ver Usuarios</a></li>
            <li><a href='/productos'>Ver Productos</a></li>
            <li><a href='/test_db'>Probar conexión a la BD</a></li>
        </ul>
    """

# Verificar conexión con la BD
@app.route('/test_db')
def test_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        return f"<h2>Conexión exitosa a la base de datos: {db_name[0]}</h2>"
    except Exception as e:
        return f"<h2>Error en la conexión: {e}</h2>"

# Listar usuarios
@app.route('/usuarios')
def usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios;")
        rows = cursor.fetchall()

        html = "<h1>Usuarios registrados</h1>"
        html += "<table border='1'><tr><th>ID</th><th>Nombre</th><th>Email</th></tr>"
        for row in rows:
            html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
        html += "</table>"

        return html
    except Exception as e:
        return f"<h2>Error al obtener usuarios: {e}</h2>"

# Listar productos
@app.route('/productos')
def productos():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos;")
        rows = cursor.fetchall()

        html = "<h1>Productos registrados</h1>"
        html += "<table border='1'><tr><th>ID</th><th>Nombre</th><th>Talla</th><th>Precio</th><th>Stock</th></tr>"
        for row in rows:
            html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
        html += "</table>"

        return html
    except Exception as e:
        return f"<h2>Error al obtener productos: {e}</h2>"

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
