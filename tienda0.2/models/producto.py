"""Modelo que representa un producto del inventario."""

from persistent import Persistent
from models.categoria import Categoria
from models.proveedor import Proveedor


class Producto(Persistent):
    """Representa un artículo comercializable almacenado en el inventario."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        descripcion: str,
        precio: float,
        existencias: int,
        categoria: Categoria,
        proveedor: Proveedor,
    ) -> None:
        super().__init__()
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.existencias = existencias
        self.categoria = categoria
        self.proveedor = proveedor

    def incrementar_existencias(self, cantidad: int) -> None:
        """Incrementa el inventario disponible del producto."""
        if cantidad <= 0:
            raise ValueError("La cantidad a incrementar debe ser mayor a cero.")
        self.existencias += cantidad
        self._p_changed = True

    def disminuir_existencias(self, cantidad: int) -> bool:
        """Disminuye las existencias tras validar suficiencia en stock."""
        if self.verificar_disponibilidad(cantidad):
            self.existencias -= cantidad
            self._p_changed = True
            return True
        return False

    def verificar_disponibilidad(self, cantidad_requerida: int) -> bool:
        """Valida si existen suficientes unidades en inventario."""
        return self.existencias >= cantidad_requerida

    def actualizar_precio(self, nuevo_precio: float) -> None:
        """Actualiza la tarifa de venta del producto."""
        if nuevo_precio <= 0:
            raise ValueError("El precio debe ser un número estrictamente positivo.")
        self.precio = nuevo_precio
        self._p_changed = True

    def __repr__(self) -> str:
        return f"<Producto: {self.nombre} | Stock: {self.existencias} | Precio: ${self.precio:.2f}>"