"""Módulo especializado en consultas y reportes del sistema."""

from datetime import date
from typing import List, Dict
from models.producto import Producto
from models.venta import Venta
from persistence.zodb_manager import (
    ZODBManager,
    CONTENEDOR_PRODUCTOS,
    CONTENEDOR_VENTAS,
)

UMBRAL_STOCK_BAJO_DEFAULT: int = 5


class TiendaQueries:
    """Proporciona consultas avanzadas y filtros sobre los objetos persistidos."""

    def __init__(self, db_manager: ZODBManager) -> None:
        self.db_manager = db_manager

    def obtener_todos_los_productos(self) -> List[Producto]:
        """Obtiene la lista completa de productos registrados en el catálogo."""
        if CONTENEDOR_PRODUCTOS not in self.db_manager.root:
            return []
        return list(self.db_manager.root[CONTENEDOR_PRODUCTOS].values())

    def productos_disponibles(self) -> List[Producto]:
        """Obtiene únicamente los productos con existencias en stock mayores a 0."""
        return [p for p in self.obtener_todos_los_productos() if p.existencias > 0]

    def productos_bajo_stock(self, umbral: int = UMBRAL_STOCK_BAJO_DEFAULT) -> List[Producto]:
        """Recupera productos cuyas existencias sean estrictamente menores a un umbral."""
        return [p for p in self.obtener_todos_los_productos() if p.existencias < umbral]

    def productos_por_precio_minimo(self, precio_minimo: float) -> List[Producto]:
        """Filtra productos cuyo precio sea estrictamente mayor al límite dado."""
        return [p for p in self.obtener_todos_los_productos() if p.precio > precio_minimo]

    def productos_por_proveedor(self, id_proveedor: str) -> List[Producto]:
        """Obtiene los productos surtidos por un proveedor en específico."""
        return [
            p for p in self.obtener_todos_los_productos()
            if p.proveedor and p.proveedor.id_proveedor == id_proveedor
        ]

    def ventas_por_cliente(self, id_cliente: str) -> List[Venta]:
        """Obtiene el historial de compras efectuadas por un determinado cliente."""
        if CONTENEDOR_VENTAS not in self.db_manager.root:
            return []
        return [
            v for v in self.db_manager.root[CONTENEDOR_VENTAS].values()
            if v.cliente and v.cliente.id_cliente == id_cliente
        ]

    def productos_mas_vendidos(self) -> Dict[str, int]:
        """Genera un reporte acumulado con la cantidad total vendida por cada producto."""
        resumen_ventas: Dict[str, int] = {}
        if CONTENEDOR_VENTAS not in self.db_manager.root:
            return resumen_ventas

        for venta in self.db_manager.root[CONTENEDOR_VENTAS].values():
            for detalle in venta.detalles:
                nombre_prod = detalle.producto.nombre
                resumen_ventas[nombre_prod] = (
                    resumen_ventas.get(nombre_prod, 0) + detalle.cantidad
                )
        return dict(sorted(resumen_ventas.items(), key=lambda item: item[1], reverse=True))

    def calcular_total_ventas_diarias(self, fecha_consulta: date) -> float:
        """Suma el importe neto total de las ventas procesadas en una fecha dada."""
        if CONTENEDOR_VENTAS not in self.db_manager.root:
            return 0.0
        return sum(
            v.total for v in self.db_manager.root[CONTENEDOR_VENTAS].values()
            if v.fecha_hora.date() == fecha_consulta
        )