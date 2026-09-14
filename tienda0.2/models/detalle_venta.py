"""Modelo que representa una línea de detalle dentro de una venta."""

from persistent import Persistent
from models.producto import Producto


class DetalleVenta(Persistent):
    """Representa la partida individual dentro de un comprobante de venta."""

    def __init__(self, id_detalle: str, producto: Producto, cantidad: int) -> None:
        super().__init__()
        self.id_detalle = id_detalle
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = producto.precio

    def calcular_subtotal_linea(self) -> float:
        """Calcula el subtotal acumulado de esta partida."""
        return self.cantidad * self.precio_unitario

    def __repr__(self) -> str:
        return (
            f"<Detalle: {self.producto.nombre} x{self.cantidad} "
            f"@ ${self.precio_unitario:.2f} = ${self.calcular_subtotal_linea():.2f}>"
        )