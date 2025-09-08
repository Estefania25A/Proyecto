from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, json, csv, sqlite3

app = Flask(__name__)

# ---------------- RUTAS DE ARCHIVOS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
DB_PATH = os.path.join(BASE_DIR, "database", "inventario.db")

# ---------------- BASE DE DATOS ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    data = cursor.fetchall()
    conn.close()
    return data

def add_product(nombre, cantidad, precio, descripcion):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre, cantidad, precio, descripcion) VALUES (?, ?, ?, ?)",
                   (nombre, cantidad, precio, descripcion))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

# ---------------- EXPORTAR DATOS ----------------
def export_txt():
    productos = get_all_products()
    with open(os.path.join(DATOS_DIR, "datos.txt"), "w", encoding="utf-8") as f:
        for p in productos:
            f.write(f"{p[0]}, {p[1]}, {p[2]}, {p[3]}, {p[4]}\n")

def export_json():
    productos = get_all_products()
    data = [
        {"id": p[0], "nombre": p[1], "cantidad": p[2], "precio": p[3], "descripcion": p[4]}
        for p in productos
    ]
    with open(os.path.join(DATOS_DIR, "datos.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def export_csv():
    productos = get_all_products()
    archivo = os.path.join(DATOS_DIR, "datos.csv")
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Producto", "Cantidad", "Precio", "Descripción"])
        writer.writerows(productos)

# ---------------- RUTAS FLASK ----------------
@app.route("/")
def index():
    productos = get_all_products()
    return render_template("index.html", productos=productos)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        descripcion = request.form["descripcion"]
        add_product(nombre, cantidad, precio, descripcion)
        return redirect(url_for("index"))
    return render_template("products/form.html")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_product(id)
    return redirect(url_for("index"))

# ----- Rutas para exportar -----
@app.route("/export/txt")
def ver_txt():
    export_txt()
    with open(os.path.join(DATOS_DIR, "datos.txt"), "r", encoding="utf-8") as f:
        return "<br>".join(f.readlines())

@app.route("/export/json")
def ver_json():
    export_json()
    with open(os.path.join(DATOS_DIR, "datos.json"), "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/export/csv")
def ver_csv():
    export_csv()
    with open(os.path.join(DATOS_DIR, "datos.csv"), "r", encoding="utf-8") as f:
        return "<pre>" + f.read() + "</pre>"

# ---------------- INICIO ----------------
if __name__ == "__main__":
    os.makedirs(DATOS_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    init_db()
    app.run(debug=True)


