from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from inventario import Producto, Inventario

app = Flask(__name__)

# Crear instancia de inventario en memoria
inventario = Inventario()

# --- Inicializar base de datos ---
def init_db():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Ruta principal ---
@app.route("/")
def index():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template("index.html", productos=productos)

# --- Agregar producto ---
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = int(request.form["cantidad"])
        precio = float(request.form["precio"])
        descripcion = request.form["descripcion"]

        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, precio, descripcion) VALUES (?, ?, ?, ?)",
            (nombre, cantidad, precio, descripcion)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html")

# --- Eliminar producto ---
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

