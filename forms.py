from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

# --- Formulario con FlaskForm (para /productos/nuevo y /productos/editar) ---
class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=0)])
    precio = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Guardar')


# --- Función auxiliar (si quieres validar a mano con request.form) ---
def parse_producto_form(form):
    """
    Valida y convierte los campos del formulario de producto.
    Devuelve (data, errores) donde data es un dict listo para usar.
    """
    errores = []
    nombre = (form.get("nombre") or "").strip()

    try:
        cantidad = int(form.get("cantidad", "").strip())
        if cantidad < 0:
            errores.append("La cantidad no puede ser negativa.")
    except ValueError:
        errores.append("La cantidad debe ser un número entero.")

    try:
        precio = float(form.get("precio", "").strip())
        if precio < 0:
            errores.append("El precio no puede ser negativo.")
    except ValueError:
        errores.append("El precio debe ser un número (usa punto decimal).")

    if not nombre:
        errores.append("El nombre es obligatorio.")

    return ({"nombre": nombre, "cantidad": cantidad if not errores else 0,
             "precio": precio if not errores else 0.0}, errores)
