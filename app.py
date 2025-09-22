# app.py (sin SQLAlchemy, usando mysql.connector)
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from conexion.conexion import conexion, cerrar_conexion
from forms import ProductoForm, parse_producto_form   # ✅ corregido
from models.model_login import Usuario


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'   # En producción usa variable de entorno

# --- CSRF global ---
csrf = CSRFProtect(app)

# --- Flask-Login ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # adonde redirigir si no hay sesión

@login_manager.user_loader
def load_user(user_id: str):
    try:
        return Usuario.obtener_por_id(int(user_id))
    except Exception:
        return None


# ========================
#  AUTENTICACIÓN
# ========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = Usuario.obtener_por_mail(email)
            if not user:
                flash('Credenciales inválidas. Inténtalo de nuevo.', 'danger')
                return render_template('login.html', title='Iniciar Sesión')

            from werkzeug.security import check_password_hash
            ok = check_password_hash(user.password_hash, password)

            if ok:
                login_user(user)
                flash('Has iniciado sesión correctamente.', 'success')
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash('Credenciales inválidas. Inténtalo de nuevo.', 'danger')

        except Exception:
            import traceback; traceback.print_exc()
            flash('Error al iniciar sesión (revisa la consola).', 'danger')

    return render_template('login.html', title='Iniciar Sesión')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre','').strip()
        email  = request.form.get('email','').strip().lower()
        password  = request.form.get('password','')
        password2 = request.form.get('password2','')

        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('registro.html', title='Registro', nombre=nombre, email=email)

        if password != password2:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('registro.html', title='Registro', nombre=nombre, email=email)

        if Usuario.obtener_por_mail(email):
            flash('El correo ya está registrado.', 'warning')
            return render_template('registro.html', title='Registro', nombre=nombre, email=email)

        user = Usuario.crear_usuario(email=email, password_plano=password, nombre=nombre)
        if user:
            flash('Usuario creado. Ahora inicia sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No se pudo registrar.', 'danger')

    return render_template('registro.html', title='Registro')


# ========================
#  CONTEXTO / PÁGINAS BASE
# ========================
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@app.route('/')
@login_required
def index():
    return render_template('index.html', title='Inicio')

@app.route('/usuario/<nombre>')
@login_required
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/about/')
@login_required
def about():
    return render_template('about.html', title='Acerca de')


# ========================
#  PRODUCTOS (CRUD)
# ========================
@app.route('/productos')
@login_required
def listar_productos():
    q = request.args.get('q', '').strip()
    conn = conexion()
    cur = conn.cursor(dictionary=True)
    try:
        if q:
            cur.execute(
                "SELECT id, nombre, cantidad, precio FROM productos WHERE nombre LIKE %s",
                (f"%{q}%",)
            )
        else:
            cur.execute("SELECT id, nombre, cantidad, precio FROM productos")
        productos = cur.fetchall()
        return render_template('productos/list.html', title='Productos', productos=productos, q=q)
    finally:
        cur.close()
        cerrar_conexion(conn)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        conn = conexion()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
                (form.nombre.data.strip(), form.cantidad.data, float(form.precio.data))
            )
            conn.commit()
            flash('Producto agregado correctamente.', 'success')
            return redirect(url_for('listar_productos'))
        except Exception as e:
            conn.rollback()
            form.nombre.errors.append('No se pudo guardar: ' + str(e))
        finally:
            cur.close()
            cerrar_conexion(conn)
    return render_template('productos/form.html', title='Nuevo producto', form=form, modo='crear')


@app.route('/productos/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def editar_producto(pid):
    conn = conexion()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, nombre, cantidad, precio FROM productos WHERE id = %s", (pid,))
        prod = cur.fetchone()
        if not prod:
            flash('Producto no encontrado.', 'warning')
            return redirect(url_for('listar_productos'))

        form = ProductoForm(data={'nombre': prod['nombre'], 'cantidad': prod['cantidad'], 'precio': prod['precio']})

        if form.validate_on_submit():
            nombre = form.nombre.data.strip()
            cantidad = form.cantidad.data
            precio = float(form.precio.data)
            cur2 = conn.cursor()
            try:
                cur2.execute(
                    "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s",
                    (nombre, cantidad, precio, pid)
                )
                conn.commit()
                flash('Producto actualizado correctamente.', 'success')
                return redirect(url_for('listar_productos'))
            except Exception as e:
                conn.rollback()
                form.nombre.errors.append('Error al actualizar: ' + str(e))
            finally:
                cur2.close()

        return render_template('productos/form.html', title='Editar producto', form=form, modo='editar', pid=pid)
    finally:
        cur.close()
        cerrar_conexion(conn)


@app.route('/productos/<int:pid>/eliminar', methods=['POST'])
@login_required
def eliminar_producto(pid):
    conn = conexion()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM productos WHERE id = %s", (pid,))
        if cur.rowcount > 0:
            conn.commit()
            flash('Producto eliminado correctamente.', 'success')
        else:
            flash('Producto no encontrado.', 'warning')
        return redirect(url_for('listar_productos'))
    finally:
        cur.close()
        cerrar_conexion(conn)


# ========================
#  MAIN
# ========================
if __name__ == '__main__':
    app.run(debug=True)
