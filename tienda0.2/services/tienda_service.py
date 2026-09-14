"""Módulo que contiene la lógica de negocio del sistema de tienda."""

from typing import List
from models.categoria import Categoria
from models.proveedor import Proveedor
from models.cliente import Cliente
from models.producto import Producto
from models.venta import Venta
from persistence.zodb_manager import (
    ZODBManager,
    CONTENEDOR_CATEGORIAS,
    CONTENEDOR_PROVEEDORES,
    CONTENEDOR_PRODUCTOS,
    CONTENEDOR_CLIENTES,
    CONTENEDOR_VENTAS,
)


class TiendaService:
    """Coordina las operaciones operativas y reglas de negocio del sistema."""

    def __init__(self, db_manager: ZODBManager) -> None:
        self.db_manager = db_manager

    def registrar_categoria(self, id_categoria: str, nombre: str, descripcion: str) -> Categoria:
        """Registra una nueva categoría en la BDOO."""
        if not id_categoria or not nombre:
            raise ValueError("El ID y nombre de categoría no pueden estar vacíos.")
        categoria = Categoria(id_categoria, nombre, descripcion)
        self.db_manager.guardar_objeto(CONTENEDOR_CATEGORIAS, id_categoria, categoria)
        return categoria

    def registrar_proveedor(
        self, id_proveedor: str, rfc: str, razon_social: str, telefono: str, email: str
    ) -> Proveedor:
        """Registra un nuevo proveedor en el sistema."""
        if not id_proveedor or not rfc or not razon_social:
            raise ValueError("Datos obligatorios de proveedor incompletos.")
        proveedor = Proveedor(id_proveedor, rfc, razon_social, telefono, email)
        self.db_manager.guardar_objeto(CONTENEDOR_PROVEEDORES, id_proveedor, proveedor)
        return proveedor

    def registrar_cliente(
        self, id_cliente: str, nombre: str, telefono: str, email: str, direccion: str
    ) -> Cliente:
        """Registra un nuevo cliente en el catálogo."""
        if not id_cliente or not nombre:
            raise ValueError("El ID y nombre del cliente son requeridos.")
        cliente = Cliente(id_cliente, nombre, telefono, email, direccion)
        self.db_manager.guardar_objeto(CONTENEDOR_CLIENTES, id_cliente, cliente)
        return cliente

    def registrar_producto(
        self,
        codigo: str,
        nombre: str,
        descripcion: str,
        precio: float,
        existencias: int,
        id_categoria: str,
        id_proveedor: str,
    ) -> Producto:
        """Registra un nuevo producto asociando su categoría y proveedor."""
        if precio <= 0:
            raise ValueError("El precio debe ser un número positivo.")
        if existencias < 0:
            raise ValueError("Las existencias no pueden ser negativas.")

        categoria = self.db_manager.obtener_objeto(CONTENEDOR_CATEGORIAS, id_categoria)
        if not categoria:
            raise KeyError(f"La categoría con ID '{id_categoria}' no fue encontrada.")

        proveedor = self.db_manager.obtener_objeto(CONTENEDOR_PROVEEDORES, id_proveedor)
        if not proveedor:
            raise KeyError(f"El proveedor con ID '{id_proveedor}' no fue encontrado.")

        producto = Producto(
            codigo, nombre, descripcion, precio, existencias, categoria, proveedor
        )
        self.db_manager.guardar_objeto(CONTENEDOR_PRODUCTOS, codigo, producto)
        return producto

    def actualizar_inventario(self, codigo_producto: str, incremento: int) -> int:
        """Incrementa las existencias de un producto específico."""
        producto: Producto = self.db_manager.obtener_objeto(CONTENEDOR_PRODUCTOS, codigo_producto)
        if not producto:
            raise KeyError(f"Producto con código '{codigo_producto}' no existe.")

        producto.incrementar_existencias(incremento)
        self.db_manager.hacer_commit()
        return producto.existencias

    def registrar_venta(self, folio_venta: str, id_cliente: str, items: List[tuple]) -> Venta:
        """Procesa una transacción de venta descontando stock e ingresando la venta."""
        cliente = self.db_manager.obtener_objeto(CONTENEDOR_CLIENTES, id_cliente)
        if not cliente:
            raise KeyError(f"El cliente con ID '{id_cliente}' no está registrado.")

        venta = Venta(folio_venta, cliente)

        for codigo_prod, cantidad in items:
            producto: Producto = self.db_manager.obtener_objeto(CONTENEDOR_PRODUCTOS, codigo_prod)
            if not producto:
                raise KeyError(f"El producto con código '{codigo_prod}' no existe.")
            
            exito = venta.agregar_producto(producto, cantidad)
            if not exito:
                raise ValueError(
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible: {producto.existencias}, Solicitado: {cantidad}"
                )

        self.db_manager.guardar_objeto(CONTENEDOR_VENTAS, folio_venta, venta)
        return venta