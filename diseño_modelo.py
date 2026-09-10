import os
import transaction
from persistent import Persistent
from persistent.list import PersistentList
from ZODB import DB, FileStorage


# 1. DEFINICIÓN DE CLASES (MODELADO BDOO)
class Persona(Persistent):
    """Superclase Base"""
    def __init__(self, id_persona: str, nombre: str, email: str):
        self.id_persona = id_persona
        self.nombre = nombre
        self.email = email

class Estudiante(Persona):
    """Subclase que hereda de Persona"""
    def __init__(self, id_persona: str, nombre: str, email: str, matricula: str, carrera: str):
        super().__init__(id_persona, nombre, email)
        self.matricula = matricula
        self.carrera = carrera

    def __str__(self):
        return f"Estudiante({self.matricula}): {self.nombre} - {self.carrera}"

class Curso(Persistent):
    """Clase que mantiene referencias a objetos Estudiante"""
    def __init__(self, codigo: str, nombre_curso: str):
        self.codigo = codigo
        self.nombre_curso = nombre_curso
        self.estudiantes = PersistentList()  # Colección persistente de objetos

    def agregar_estudiante(self, estudiante: Estudiante):
        self.estudiantes.append(estudiante)

    def __str__(self):
        return f"Curso({self.codigo}): {self.nombre_curso} | Inscritos: {len(self.estudiantes)}"

# 2. GESTOR DE PERSISTENCIA (OPERACIONES CRUD)
class SistemaBDOO:
    def __init__(self, db_path="universidad.fs"):
        self.storage = FileStorage.FileStorage(db_path)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

        # Inicializar contenedores principales si no existen
        if 'estudiantes' not in self.root:
            self.root['estudiantes'] = {}
        if 'cursos' not in self.root:
            self.root['cursos'] = {}
        transaction.commit()

    # --- CREATE ---
    def crear_estudiante(self, id_p: str, nombre: str, email: str, matricula: str, carrera: str):
        if matricula in self.root['estudiantes']:
            print(f"El estudiante con matrícula {matricula} ya existe.")
            return None
        nuevo_estudiante = Estudiante(id_p, nombre, email, matricula, carrera)
        self.root['estudiantes'][matricula] = nuevo_estudiante
        transaction.commit()
        print(f"Creado: {nuevo_estudiante}")
        return nuevo_estudiante

    def crear_curso(self, codigo: str, nombre: str):
        if codigo in self.root['cursos']:
            print(f"El curso {codigo} ya existe.")
            return None
        nuevo_curso = Curso(codigo, nombre)
        self.root['cursos'][codigo] = nuevo_curso
        transaction.commit()
        print(f"Creado: {nuevo_curso}")
        return nuevo_curso

    # --- READ ---
    def obtener_estudiante(self, matricula: str):
        estudiante = self.root['estudiantes'].get(matricula)
        if estudiante:
            print(f"Encontrado: {estudiante}")
        else:
            print(f"Estudiante {matricula} no encontrado.")
        return estudiante

    def listar_estudiantes(self):
        print("\nLista de Estudiantes:")
        for est in self.root['estudiantes'].values():
            print(f"{est}")

    # --- UPDATE ---
    def actualizar_carrera_estudiante(self, matricula: str, nueva_carrera: str):
        estudiante = self.root['estudiantes'].get(matricula)
        if estudiante:
            estudiante.carrera = nueva_carrera
            transaction.commit()
            print(f"Actualizada carrera de {estudiante.nombre} a '{nueva_carrera}'")
        else:
            print("No se pudo actualizar: Estudiante no encontrado.")

    # --- DELETE ---
    def eliminar_estudiante(self, matricula: str):
        if matricula in self.root['estudiantes']:
            est = self.root['estudiantes'].pop(matricula)
            # Eliminarlo también de los cursos donde esté inscrito
            for curso in self.root['cursos'].values():
                if est in curso.estudiantes:
                    curso.estudiantes.remove(est)
            transaction.commit()
            print(f"Estudiante {matricula} eliminado de la BDOO.")
        else:
            print("No se pudo eliminar: Estudiante no encontrado.")

    def cerrar(self):
        self.connection.close()
        self.db.close()
        self.storage.close()

# 3. DEMOSTRACIÓN DEL FLUJO CRUD

if __name__ == "__main__":
    sistema = SistemaBDOO()

    print("OPERACIONES CREATE")
    e1 = sistema.crear_estudiante("P001", "Ana Martínez", "ana@example.com", "S2001", "Ingeniería de Software")
    e2 = sistema.crear_estudiante("P002", "Carlos Gómez", "carlos@example.com", "S2002", "Inteligencia Artificial")
    
    c1 = sistema.crear_curso("CC101", "Bases de Datos Avanzadas")
    if c1 and e1:
        c1.agregar_estudiante(e1)
        transaction.commit()

    print("\nOPERACIONES READ")
    sistema.obtener_estudiante("S2001")
    sistema.listar_estudiantes()

    print("\nOPERACIONES UPDATE")
    sistema.actualizar_carrera_estudiante("S2001", "Ciencia de Datos")
    sistema.obtener_estudiante("S2001")

    print("\nOPERACIONES DELETE")
    sistema.eliminar_estudiante("S2002")
    sistema.listar_estudiantes()

    sistema.cerrar()