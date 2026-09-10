import os
import ZODB
from ZODB.FileStorage import FileStorage
import transaction
from persistent.mapping import PersistentMapping

def abrir_base_datos():

    os.makedirs("./base_datos", exist_ok=True)

    storage = FileStorage("./base_datos/biblioteca.fs")
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()

    return db, connection, root

def inicializar_base_datos(root): 
    if not hasattr(root, "autores"): 
        root.autores = PersistentMapping() 

    if not hasattr(root, "libros"): 
        root.libros = PersistentMapping() 

    if not hasattr(root, "estudiantes"): 
            root.estudiantes = PersistentMapping() 

    if not hasattr(root, "prestamos"): 
        root.prestamos = PersistentMapping() 

    transaction.commit()

def cerrar_base_datos(db: ZODB.DB, connection):
    connection.close()
    db.close()