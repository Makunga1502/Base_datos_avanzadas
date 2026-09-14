import sys
from pathlib import Path

# Registra la carpeta del proyecto en la ruta de búsqueda de Python
sys.path.append(str(Path(__file__).resolve().parent))

from datetime import datetime
from persistence.zodb_manager import ZODBManager
from services.tienda_service import TiendaService
from queries.tienda_queries import TiendaQueries


def ejecutar_demostracion() -> None:
    """Ejecuta un ciclo completo demostrando la modularidad del sistema."""
    archivo_db = "tienda_refactorizada.fs"
    db_manager = ZODBManager(archivo_db)

    
    print("INICIANDO SISTEMA TIENDA REFACTORIZADO (ARQUITECTURA MODULAR)")


    try:
        db_manager.abrir_conexion()
        service = TiendaService(db_manager)
        queries = TiendaQueries(db_manager)

        # 1. Registro de entidades mediante Servicio
        cat1 = service.registrar_categoria("CAT-01", "Electrónica", "Aparatos electrónicos")
        prov1 = service.registrar_proveedor(
            "PROV-01", "TECH123456ABC", "Tech Supplier S.A.", "555-0192", "contacto@tech.com"
        )
        cli1 = service.registrar_cliente(
            "CLI-01", "María López", "555-9876", "maria@gmail.com", "Av. Reforma #45"
        )

        prod1 = service.registrar_producto(
            codigo="PROD-01",
            nombre="Laptop Pro 15",
            descripcion="16GB RAM, 512GB SSD",
            precio=24500.00,
            existencias=10,
            id_categoria="CAT-01",
            id_proveedor="PROV-01",
        )
        
        prod2 = service.registrar_producto(
            codigo="PROD-02",
            nombre="Mouse Ergonómico",
            descripcion="Mouse inalámbrico silencioso",
            precio=550.00,
            existencias=3,  # Stock bajo
            id_categoria="CAT-01",
            id_proveedor="PROV-01",
        )

        print("Registros iniciales almacenados en ZODB exitosamente.")

        # 2. Registrar Venta con lógica de negocio
        items_compra = [("PROD-01", 2), ("PROD-02", 1)]
        venta1 = service.registrar_venta("VEN-1001", "CLI-01", items_compra)
        print(f"Venta procesada con éxito: {venta1}")

        # 3. Consultas Especializadas
        print("\nRESULTADOS DE CONSULTAS REFACTORIZADAS ---")
        print(f"• Productos con stock crítico (<5): {queries.productos_bajo_stock()}")
        print(f"• Historial de ventas de María López: {queries.ventas_por_cliente('CLI-01')}")
        print(f"• Reporte productos más vendidos: {queries.productos_mas_vendidos()}")
        print(f"• Total ventas del día de hoy: ${queries.calcular_total_ventas_diarias(datetime.now().date()):.2f}")

    except Exception as error:
        print(f"Ocurrió un error en el sistema: {error}")
    finally:
        db_manager.cerrar_conexion()
        print("\nConexión ZODB cerrada correctamente.")


if __name__ == "__main__":
    ejecutar_demostracion()