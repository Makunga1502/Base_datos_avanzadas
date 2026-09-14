"""Modelo que representa una categoría de productos."""

from persistent import Persistent


class Categoria(Persistent):
    """Representa la clasificación lógica a la que pertenece un producto."""

    def __init__(self, id_categoria: str, nombre: str, descripcion: str) -> None:
        super().__init__()
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self) -> str:
        return f"<Categoria: {self.nombre} (ID: {self.id_categoria})>"