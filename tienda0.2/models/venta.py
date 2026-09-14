"""Modelo que representa una transacción de venta comercial."""

from datetime import datetime
from typing import List
from persistent import Persistent
from persistent.list import PersistentList
from models.cliente import Cliente
from models.detalle_venta import DetalleVenta
from models.producto import Producto


class Venta(Persistent):
    """Representa la nota de venta o factura efectuada a un cliente."""

    PORCENTAJE_IVA_DEFAULT: float = 0.16

    def __init__(self, folio_venta: str, cliente: Cliente) -> None:
        super().__init__()
        self.folio_venta = folio_venta
        self.fecha_hora = datetime.now()
        self.cliente = cliente
        self.detalles: PersistentList = PersistentList()
        self.subtotal: float = 0.0
        self.total: float = 0.0

    def agregar_producto(self, producto: Producto, cantidad: int) -> bool:
        """Añade una línea de producto a la venta disminuyendo el inventario."""
        if producto.disminuir_existencias(cantidad):
            id_det = f"DET-{self.folio_venta}-{len(self.detalles) + 1}"
            detalle = DetalleVenta(id_det, producto, cantidad)
            self.detalles.append(detalle)
            self.subtotal = self.calcular_subtotal()
            self.total = self.calcular_total(self.PORCENTAJE_IVA_DEFAULT)
            self._p_changed = True
            return True
        return False

    def calcular_subtotal(self) -> float:
        """Suma los subtotales de cada línea de detalle incluida."""
        return sum(d.calcular_subtotal_linea() for d in self.detalles)

    def calcular_total(self, porcentaje_impuesto: float = PORCENTAJE_IVA_DEFAULT) -> float:
        """Aplica el porcentaje impositivo sobre el subtotal calculado."""
        return self.calcular_subtotal() * (1.0 + porcentaje_impuesto)

    def consultar_productos(self) -> List[DetalleVenta]:
        """Recupera la lista de desgloses de la venta."""
        return list(self.detalles)

    def __repr__(self) -> str:
        return (
            f"<Venta: Folio {self.folio_venta} | Cliente: {self.cliente.nombre} "
            f"| Total: ${self.total:.2f}>"
        )