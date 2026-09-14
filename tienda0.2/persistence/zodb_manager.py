"""Gestor responsable de la apertura, commit y cierre de ZODB."""

import os
from typing import Optional, Any
import transaction
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from ZODB import FileStorage, DB

RUTA_BASE_DATOS_DEFAULT: str = "tienda.fs"
CONTENEDOR_CATEGORIAS: str = "categorias"
CONTENEDOR_PROVEEDORES: str = "proveedores"
CONTENEDOR_PRODUCTOS: str = "productos"
CONTENEDOR_CLIENTES: str = "clientes"
CONTENEDOR_VENTAS: str = "ventas"


class ZODBManager:
    """Administra las conexiones, transacciones y contenedores OOBTree en ZODB."""

    def __init__(self, archivo_db: str = RUTA_BASE_DATOS_DEFAULT) -> None:
        self.archivo_db = archivo_db
        self.storage: Optional[FileStorage.FileStorage] = None
        self.db: Optional[DB] = None
        self.connection: Optional[Any] = None
        self.root: Optional[Any] = None

    def abrir_conexion(self) -> None:
        """Abre el archivo de almacenamiento, conecta la DB e inicializa raíces."""
        try:
            self.storage = FileStorage.FileStorage(self.archivo_db)
            self.db = DB(self.storage)
            self.connection = self.db.open()
            self.root = self.connection.root()
            self._inicializar_contenedores()
        except Exception as error:
            raise RuntimeError(f"Fallo al abrir la conexión con ZODB: {error}") from error

    def _inicializar_contenedores(self) -> None:
        """Garantiza la existencia de estructuras BTree principales."""
        contenedores = [
            CONTENEDOR_CATEGORIAS,
            CONTENEDOR_PROVEEDORES,
            CONTENEDOR_PRODUCTOS,
            CONTENEDOR_CLIENTES,
            CONTENEDOR_VENTAS,
        ]
        se_requiere_commit = False
        for c in contenedores:
            if c not in self.root:
                self.root[c] = OOBTree()
                se_requiere_commit = True
        if se_requiere_commit:
            self.hacer_commit()

    def hacer_commit(self) -> None:
        """Persiste permanentemente los cambios pendientes en disco."""
        transaction.commit()

    def hacer_rollback(self) -> None:
        """Aborta la transacción actual descartando cambios no confirmados."""
        transaction.abort()

    def cerrar_conexion(self) -> None:
        """Cierra de forma segura conexiones y almacenamiento."""
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.db:
            self.db.close()
            self.db = None
        if self.storage:
            self.storage.close()
            self.storage = None

    def guardar_objeto(self, contenedor: str, clave: str, objeto: Persistent) -> None:
        """Guarda un objeto dentro de un contenedor OOBTree específico."""
        if contenedor not in self.root:
            raise KeyError(f"El contenedor '{contenedor}' no existe en ZODB.")
        self.root[contenedor][clave] = objeto
        self.hacer_commit()

    def obtener_objeto(self, contenedor: str, clave: str) -> Optional[Persistent]:
        """Obtiene una referencia persistente dado su contenedor y clave."""
        if contenedor not in self.root:
            return None
        return self.root[contenedor].get(clave, None)

    def eliminar_objeto(self, contenedor: str, clave: str) -> bool:
        """Remueve una entidad de su contenedor BTree."""
        if contenedor in self.root and clave in self.root[contenedor]:
            del self.root[contenedor][clave]
            self.hacer_commit()
            return True
        return False