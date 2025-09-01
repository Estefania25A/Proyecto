class Producto:
    def __init__(self, id_producto, nombre, cantidad, precio, descripcion=""):
        self.id_producto = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.descripcion = descripcion

    def __repr__(self):
        return f"{self.nombre} - {self.cantidad} unidades - ${self.precio}"


class Inventario:
    def __init__(self):
        self.productos = {}  # diccionario {id: Producto}

    def agregar_producto(self, producto):
        self.productos[producto.id_producto] = producto

    def eliminar_producto(self, id_producto):
        if id_producto in self.productos:
            del self.productos[id_producto]

    def actualizar_producto(self, id_producto, cantidad=None, precio=None, descripcion=None):
        if id_producto in self.productos:
            if cantidad is not None:
                self.productos[id_producto].cantidad = cantidad
            if precio is not None:
                self.productos[id_producto].precio = precio
            if descripcion is not None:
                self.productos[id_producto].descripcion = descripcion

    def buscar_producto(self, nombre):
        return [p for p in self.productos.values() if nombre.lower() in p.nombre.lower()]

    def mostrar_todos(self):
        return list(self.productos.values())
