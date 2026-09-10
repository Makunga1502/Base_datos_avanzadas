import ZODB
import ZODB.FileStorage
import transaction
from BTrees._OOBTree import OOBTree
from modelos import Autor, Libro, Estudiante, Prestamo

class SistemaBiblioteca:
    def __init__(self, archivo_db="biblioteca.fs"):
        self.storage = ZODB.FileStorage.FileStorage(archivo_db)
        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()            
        self.root = self.connection.root()

        if 'libros' not in self.root:
            self.root['libros'] = OOBTree()
        if 'estudiantes' not in self.root:
            self.root['estudiantes'] = OOBTree()
        if 'prestamos' not in self.root:
            self.root['prestamos'] = OOBTree()

        transaction.commit()

    def registrar_libro(self, isbn: str, titulo: str, anio: int, categoria: str, ejemplares: int, autores: list):
        if isbn in self.root['libros']:
            print(f"El libro con ISBN {isbn} ya está registrado.")
            return None

        libro = Libro(isbn, titulo, anio, categoria, ejemplares)
        for autor in autores:
            libro.agregar_autor(autor)

        self.root['libros'][isbn] = libro
        transaction.commit()
        print(f"Libro registrado exitosamente: {titulo}")
        return libro

    def registrar_estudiante(self, matricula: str, nombre: str, carrera: str, email: str):
        if matricula in self.root['estudiantes']:
            print(f"El estudiante con matrícula {matricula} ya está registrado.")
            return None

        estudiante = Estudiante(matricula, nombre, carrera, email)
        self.root['estudiantes'][matricula] = estudiante
        transaction.commit()
        print(f"Estudiante registrado exitosamente: {nombre}")
        return estudiante

    def registrar_prestamo(self, id_prestamo: str, isbn: str, matricula: str):
        estudiante = self.root['estudiantes'].get(matricula)
        libro = self.root['libros'].get(isbn)

        if not estudiante:
            print(f"No se encontró el estudiante con matrícula {matricula}.")
            return False
        if not libro:
            print(f"No se encontró el libro con ISBN {isbn}.")
            return False

        if libro.prestar_ejemplar():
            prestamo = Prestamo(id_prestamo, libro, estudiante)
            estudiante.agregar_prestamo(prestamo)
            self.root['prestamos'][id_prestamo] = prestamo
            transaction.commit()
            print(f"Prestamo registrado exitosamente: {id_prestamo}")
            return True
        else:
            print(f"No hay ejemplares disponibles del libro con ISBN {isbn}.")
            return False


    def restrar_devolucion(self, id_prestamo: str):
        prestamo = self.root['prestamos'].get(id_prestamo)
        if not prestamo:
            print(f"No se encontró el préstamo con ID {id_prestamo}.")
            return False

        if prestamo.estado == "devuelto":
            print(f"El préstamo con ID {id_prestamo} ya ha sido devuelto.")
            return False

        prestamo.registrar_devolucion()
        transaction.commit()
        print(f"Devolución registrada exitosamente para el préstamo con ID {id_prestamo}.")
        return True

    def buscar_libro_por_isbn(self, isbn: str):
        libro = self.root['libros'].get(isbn)
        if libro:
            autores_str = ", ".join([a.nombre for a in libro.autores])
            print(f"\n[ficha del libro]\nISBN: {libro.isbn}\nTítulo: {libro.titulo}\nAño: {libro.anio_publicacion}\nCategoría: {libro.categoria}\nEjemplares disponibles: {libro.disponibles}\nAutores: {autores_str}")
        else:
            print(f"No se encontró el libro con ISBN {isbn}.")
        return libro

    def consultar_prestamos_por_estudiante(self, matricula: str):
        estudiante = self.root['estudiantes'].get(matricula)
        if not estudiante:
            print(f"No se encontró el estudiante con matrícula {matricula}.")
            return

        print(f"\n[Préstamos del estudiante {estudiante.nombre} (Matrícula: {matricula})]")
        if not estudiante.prestamos:
            print("No hay préstamos registrados para este estudiante.")
            return

        for p in estudiante.prestamos:
            libro = p.libro
            print(f"ID Préstamo: {p.id_prestamo}, Libro: {libro.titulo}, Estado: {p.estado}, Fecha de préstamo: {p.fecha_prestamo}, Fecha de devolución: {p.fecha_devolucion}")

    def cerrar(self):
        self.connection.close()
        self.db.close()
        self.storage.close()

if __name__ == "__main__":
    sistema = SistemaBiblioteca()

    # Ejemplo de uso
    autor1 = Autor("A1", "Gabriel", "Colombiana")
    autor2 = Autor("A2", "Isabel", "Chilena")
    sistema.registrar_libro("978-3-16-148410-0", "Cien Años de Soledad", 1967, "Novela", 5, [autor1])
    sistema.registrar_libro("978-0-06-112008-4", "La Casa de los Espíritus", 1982, "Novela", 3, [autor2])

    sistema.registrar_estudiante("2023001", "Juan Pérez", "Ingeniería", "juan.perez@uabc.edu.mx")
    sistema.registrar_estudiante("2023002", "María López", "Derecho", "maria.lopez@uabc.edu.mx")

    sistema.buscar_libro_por_isbn("978-3-16-148410-0")
    sistema.consultar_prestamos_por_estudiante("2023001")
    sistema.cerrar()
    
