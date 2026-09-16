# Sistema de Gestión de Tienda en BDOO (Versión Refactorizada)

Este proyecto es una aplicación modular para la administración de inventarios, clientes, proveedores y ventas desarrollada en **Python** utilizando la base de datos orientada a objetos **ZODB (Zope Object Database)**.

Se implementó una arquitectura en capas que aplica el principio de **separación de responsabilidades**, garantizando alta mantenibilidad, reusabilidad de código y desacoplamiento para futuras extensiones (como interfaces gráficas).

---

## Arquitectura del Proyecto

El código está estructurado en 4 capas principales independientes:

```text
tienda_refactorizada/
│
├── models/                   # 1. MODELOS DEL DOMINIO
│   ├── __init__.py
│   ├── categoria.py          # Entidad Categoria (Persistent)
│   ├── proveedor.py          # Entidad Proveedor (Persistent)
│   ├── cliente.py            # Entidad Cliente (Persistent)
│   ├── producto.py           # Entidad Producto (Persistent)
│   ├── detalle_venta.py      # Entidad DetalleVenta (Persistent)
│   └── venta.py              # Entidad Venta (Persistent)
│
├── persistence/              # 2. CAPA DE PERSISTENCIA
│   ├── __init__.py
│   └── zodb_manager.py       # Gestión de conexíón ZODB, commits, rollback y OOBTree
│
├── services/                 # 3. LÓGICA DE NEGOCIO
│   ├── __init__.py
│   └── tienda_service.py     # Servicios (registrar_producto, registrar_venta, etc.)
│
├── queries/                  # 4. CAPA DE CONSULTAS Y REPORTES
│   ├── __init__.py
│   └── tienda_queries.py      # Consultas avanzadas (productos_bajo_stock, ventas, etc.)
│
├── main.py                   # Punto de entrada y prueba de integración
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Documentación técnica