from dataclasses import dataclass

@dataclass
class Producto:
    id: int | None
    nombre: str
    cantidad: int
    precio: float

    @staticmethod
    def from_row(row) -> "Producto":
        # row puede ser tuple o sqlite3.Row
        return Producto(
            id=row[0],
            nombre=row[1],
            cantidad=row[2],
            precio=row[3],
        )
