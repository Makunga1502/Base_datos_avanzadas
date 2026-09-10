import os
import transaction
from persistent import Persistent
from persistent.list import PersistentList
from BTrees.OOBTree import OOBTree
from ZODB import FileStorage, DB
from datetime import datetime


# 1. MODELOS DEL DOMINIO (PERSISTENT OBJECTS)


class Categoria(Persistent):
    def __init__(self, id_categoria: str, nombre: str, descripcion: str):
        super().__init__()
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self):
        return f"<Categoria: {self.nombre} (ID: {self.id_categoria})>"


class Proveedor(Persistent):
    def __init__(self, id_proveedor: str, rfc: str, razon_social: str, telefono: str, email: str):
        super().__init__()
        self.id_proveedor = id_proveedor
        self.rfc = rfc
        self.razon_social = razon_social
        self.telefono = telefono
        self.email = email

    def __repr__(self):
        return f"<Proveedor: {self.razon_social} (RFC: {self.rfc})>"


class Producto(Persistent):
    def __init__(self, codigo: str, nombre: str, descripcion: str, precio: float, existencias: int, categoria: Categoria, proveedor: Proveedor):
        super().__init__()
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.existencias = existencias
        self.categoria = categoria
        self.proveedor = proveedor

    # --- Métodos de Comportamiento / Lógica de Negocio ---
    def incrementar_existencias(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad a incrementar debe ser mayor a cero.")
        self.existencias += cantidad
        self._p_changed = True

    def disminuir_existencias(self, cantidad: int) -> bool:
        if self.verificar_disponibilidad(cantidad):
            self.existencias -= cantidad
            self._p_changed = True
            return True
        return False

    def verificar_disponibilidad(self, cantidad_requerida: int) -> bool:
        return self.existencias >= cantidad_requerida

    def actualizar_precio(self, nuevo_precio: float) -> None:
        if nuevo_precio <= 0:
            raise ValueError("El precio debe ser un número positivo.")
        self.precio = nuevo_precio
        self._p_changed = True

    def __repr__(self):
        return f"<Producto: {self.nombre} | Stock: {self.existencias} | Precio: ${self.precio:.2f}>"


class Cliente(Persistent):
    def __init__(self, id_cliente: str, nombre: str, telefono: str, email: str, direccion: str):
        super().__init__()
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion

    def __repr__(self):
        return f"<Cliente: {self.nombre} (ID: {self.id_cliente})>"


class DetalleVenta(Persistent):
    def __init__(self, id_detalle: str, producto: Producto, cantidad: int):
        super().__init__()
        self.id_detalle = id_detalle
        self.producto = producto
        self.cantidad = cantidad
        # Se congela el precio unitario del momento de la compra
        self.precio_unitario = producto.precio

    def calcular_subtotal_linea(self) -> float:
        return self.cantidad * self.precio_unitario

    def __repr__(self):
        return f"<Detalle: {self.producto.nombre} x{self.cantidad} @ ${self.precio_unitario:.2f} = ${self.calcular_subtotal_linea():.2f}>"


class Venta(Persistent):
    def __init__(self, folio_venta: str, cliente: Cliente):
        super().__init__()
        self.folio_venta = folio_venta
        self.fecha_hora = datetime.now()
        self.cliente = cliente
        self.detalles = PersistentList()
        self.subtotal = 0.0
        self.total = 0.0

    # --- Métodos de Comportamiento / Lógica de Negocio ---
    def agregar_producto(self, producto: Producto, cantidad: int) -> bool:
        if producto.disminuir_existencias(cantidad):
            id_det = f"DET-{self.folio_venta}-{len(self.detalles) + 1}"
            detalle = DetalleVenta(id_det, producto, cantidad)
            self.detalles.append(detalle)
            self.subtotal = self.calcular_subtotal()
            self.total = self.calcular_total(0.16)  # 16% IVA por defecto
            self._p_changed = True
            return True
        else:
            print(f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.existencias}, Requerido: {cantidad}")
            return False

    def calcular_subtotal(self) -> float:
        return sum(d.calcular_subtotal_linea() for d in self.detalles)

    def calcular_total(self, impuesto: float = 0.16) -> float:
        return self.calcular_subtotal() * (1 + impuesto)

    def consultar_productos(self) -> list:
        return list(self.detalles)

    def __repr__(self):
        return f"<Venta: Folio {self.folio_venta} | Cliente: {self.cliente.nombre} | Total: ${self.total:.2f}>"



# 2. GESTOR DE SISTEMA Y BASE DE DATOS ZODB


class SistemaTiendaBDOO:
    def __init__(self, archivo_db: str = "tienda.fs"):
        self.archivo_db = archivo_db
        self.storage = None
        self.db = None
        self.connection = None
        self.root = None

    def abrir_conexion(self):
        self.storage = FileStorage.FileStorage(self.archivo_db)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

        # Inicialización de contenedores BTree en la raíz de ZODB si no existen
        if 'categorias' not in self.root:
            self.root['categorias'] = OOBTree()
        if 'proveedores' not in self.root:
            self.root['proveedores'] = OOBTree()
        if 'productos' not in self.root:
            self.root['productos'] = OOBTree()
        if 'clientes' not in self.root:
            self.root['clientes'] = OOBTree()
        if 'ventas' not in self.root:
            self.root['ventas'] = OOBTree()
        
        transaction.commit()

    def cerrar_conexion(self):
        if self.connection:
            self.connection.close()
        if self.db:
            self.db.close()
        if self.storage:
            self.storage.close()

    # --- OPERACIONES CRUD BÁSICAS ---
    def guardar_objeto(self, clave: str, objeto: Persistent, contenedor: str):
        self.root[contenedor][clave] = objeto
        transaction.commit()

    def obtener_objeto(self, clave: str, contenedor: str):
        return self.root[contenedor].get(clave, None)

    def modificar_objeto(self, objeto: Persistent):
        objeto._p_changed = True
        transaction.commit()

    def eliminar_objeto(self, clave: str, contenedor: str):
        if clave in self.root[contenedor]:
            del self.root[contenedor][clave]
            transaction.commit()
            return True
        return False

    # --- CONSULTAS REQUERIDAS ---
    def mostrar_todos_los_productos(self):
        return list(self.root['productos'].values())

    def productos_precio_superior_a(self, precio_minimo: float):
        return [p for p in self.root['productos'].values() if p.precio > precio_minimo]

    def productos_con_existencias_menores_a(self, limite_stock: int):
        return [p for p in self.root['productos'].values() if p.existencias < limite_stock]

    def productos_por_proveedor(self, id_proveedor: str):
        return [p for p in self.root['productos'].values() if p.proveedor.id_proveedor == id_proveedor]

    def obtener_total_ventas(self) -> float:
        return sum(v.total for v in self.root['ventas'].values())



# 3. DEMOSTRACIÓN DE PERSISTENCIA Y FUNCIONALIDAD (PARTE 2)


if __name__ == "__main__":
    DB_FILE = "tienda.fs"

    # Limpieza previa de entorno si se desea empezar limpio
    if os.path.exists(DB_FILE):
        for ext in ['', '.tmp', '.old', '.index', '.lock']:
            if os.path.exists(DB_FILE + ext):
                try: os.remove(DB_FILE + ext)
                except: pass

    
    print("PASO 1: CREAR OBJETOS, GUARDAR EN ZODB Y EJECUTAR transaction.commit()")
    

    sistema = SistemaTiendaBDOO(DB_FILE)
    sistema.abrir_conexion()

    # 1. Creación e Inserción de Objetos
    cat1 = Categoria("CAT-01", "Electrónica", "Dispositivos y accesorios")
    cat2 = Categoria("CAT-02", "Abarrotes", "Alimentos no perecederos")
    sistema.guardar_objeto(cat1.id_categoria, cat1, 'categorias')
    sistema.guardar_objeto(cat2.id_categoria, cat2, 'categorias')

    prov1 = Proveedor("PROV-01", "TECH123456ABC", "Tech Supplier S.A.", "555-1122", "contacto@tech.com")
    prov2 = Proveedor("PROV-02", "FOOD987654XYZ", "Distribuidora Alimentos", "555-3344", "ventas@alimentos.com")
    sistema.guardar_objeto(prov1.id_proveedor, prov1, 'proveedores')
    sistema.guardar_objeto(prov2.id_proveedor, prov2, 'proveedores')

    p1 = Producto("PROD-01", "Laptop Gaming", "Core i7, 16GB RAM, RTX 3060", 22500.00, 10, cat1, prov1)
    p2 = Producto("PROD-02", "Mouse Inalámbrico", "Mouse óptico ergonómico", 450.00, 25, cat1, prov1)
    p3 = Producto("PROD-03", "Café Gourmet 1kg", "Café de grano tostado", 280.00, 5, cat2, prov2)
    sistema.guardar_objeto(p1.codigo, p1, 'productos')
    sistema.guardar_objeto(p2.codigo, p2, 'productos')
    sistema.guardar_objeto(p3.codigo, p3, 'productos')

    cli1 = Cliente("CLI-01", "Juan Pérez", "555-9988", "juan@gmail.com", "Av. Principal #123")
    sistema.guardar_objeto(cli1.id_cliente, cli1, 'clientes')

    # 2. Operación de Negocio: Registrar Venta y actualizar inventario
    venta1 = Venta("VEN-001", cli1)
    venta1.agregar_producto(p1, 2)  # Compra 2 laptops -> stock pasa de 10 a 8
    venta1.agregar_producto(p3, 1)  # Compra 1 café -> stock pasa de 5 a 4
    sistema.guardar_objeto(venta1.folio_venta, venta1, 'ventas')

    print("Objetos guardados con éxito. Estado previo al cierre de conexión:")
    print(f"   Venta creada: {venta1}")
    print(f"   Stock de Laptop Gaming tras venta: {p1.existencias}")

    print("\nCerrando la aplicación y la conexión a ZODB...\n")
    sistema.cerrar_conexion()
    del sistema

    # ----------------------------------------------------------------------
    
    print("PASO 2: REABRIR LA APLICACIÓN Y VERIFICAR LA PERSISTENCIA REAL")
    

    sistema_reabierto = SistemaTiendaBDOO(DB_FILE)
    sistema_reabierto.abrir_conexion()

    print("Conexión reabierta exitosamente. Recuperando datos de la BDOO...")

    # A. Mostrar todos los productos
    print("\nTODOS LOS PRODUCTOS REGISTRADOS")
    for prod in sistema_reabierto.mostrar_todos_los_productos():
        print(f"{prod.codigo}: {prod.nombre} | Categoría: {prod.categoria.nombre} | ${prod.precio:.2f} | Stock: {prod.existencias}")

    # B. Productos cuyo precio sea superior a determinada cantidad
    PRECIO_LIMITE = 500.00
    print(f"\nPRODUCTOS CON PRECIO SUPERIOR A ${PRECIO_LIMITE:.2f}")
    for prod in sistema_reabierto.productos_precio_superior_a(PRECIO_LIMITE):
        print(f"{prod.nombre} -> ${prod.precio:.2f}")

    # C. Productos con existencias menores a cierto límite
    STOCK_CRITICO = 6
    print(f"\nPRODUCTOS CON STOCK CRÍTICO (MENOR A {STOCK_CRITICO} UNIDADES)")
    for prod in sistema_reabierto.productos_con_existencias_menores_a(STOCK_CRITICO):
        print(f"{prod.nombre} -> Existencias: {prod.existencias}")

    # D. Productos proporcionados por un determinado proveedor
    print(f"\nPRODUCTOS DEL PROVEEDOR 'PROV-01' ({prov1.razon_social})")
    for prod in sistema_reabierto.productos_por_proveedor("PROV-01"):
        print(f"{prod.nombre}")

    # E. Total de ventas
    print("\nTOTAL HISTÓRICO DE VENTAS")
    total_acumulado = sistema_reabierto.obtener_total_ventas()
    print(f"Acumulado de ventas registradas: ${total_acumulado:.2f}")

    # F. Operación CRUD: Modificación y Baja
    print("\nPRUEBA DE MODIFICACIÓN Y BAJA")
    p2_recuperado = sistema_reabierto.obtener_objeto("PROD-02", "productos")
    print(f"Modificando existencias de '{p2_recuperado.nombre}' (Antes: {p2_recuperado.existencias})...")
    p2_recuperado.incrementar_existencias(10)
    sistema_reabierto.modificar_objeto(p2_recuperado)
    print(f"Stock actualizado a: {p2_recuperado.existencias}")

    sistema_reabierto.cerrar_conexion()
    print("\nDemostración completada correctamente.")