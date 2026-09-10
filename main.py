import os
import transaction
from ZODB import DB
from ZODB.FileStorage import FileStorage
from persistent import Persistent

#definición de objeto persistente
class Estudiante(Persistent):
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    def __repr__(self):
        return f"Estudiante(nombre={self.nombre}, edad={self.edad})"

def ejecutar_demo():
    print("Iniciando la demo de ZODB")
    storage = FileStorage('estudiantes.fs')
    db = DB(storage)
    connection = db.open()
    root = connection.root()

    # Crear un nuevo estudiante y agregarlo a la base de datos
    print("Agregando un nuevo estudiante a la base de datos")
    estudiante1 = Estudiante("Juan", 20)
    root['estudiante1'] = estudiante1
    transaction.commit()
    print(f"Estudiante agregado: {estudiante1}")
    print("Estudiante agregado a la base de datos")

    # Recuperar el estudiante de la base de datos
    print("Recuperando el estudiante de la base de datos")
    estudiante_recuperado = root['estudiante1']
    print(f"Estudiante recuperado: {estudiante_recuperado}")

    # buscar un estudiante que existe
    print("Buscando un estudiante que existe")
    if 'estudiante1' in root:
        print(f"Estudiante encontrado: {root['estudiante1']}")
    else:
        print("Estudiante no encontrado")
     # modificar un estudiante existente
    print("Modificando un estudiante existente")
    estudiante_recuperado.edad = 21
    transaction.commit()
    print(f"Estudiante modificado: {estudiante_recuperado}")
    print("Estudiante modificado en la base de datos")

    # eliminar un estudiante existente
    print("Eliminando un estudiante existente")
    del root['estudiante1']
    transaction.commit()
    print("Estudiante eliminado de la base de datos")

    #confirmar que el estudiante ha sido eliminado
    print("Confirmando que el estudiante ha sido eliminado")
    if 'estudiante1' not in root:
        print("Estudiante confirmado como eliminado")
    else:
        print("Error: El estudiante aún existe en la base de datos")

        #cerrar la conexión y la base de datos
    connection.close()
    db.close()

if __name__ == "__main__":
    ejecutar_demo()