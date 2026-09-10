import datetime
from persistent import Persistent
from persistent.list import PersistentList

class Autor(Persistent):
    def __init__(self, id_autor: str, nombre: str, nacionalidad: str):
        super().__init__()
        self.id_autor = id_autor
        self.nombre = nombre
        self.nacionalidad = nacionalidad

    def obtener_informacion(self) -> str:
        return f"Autor: {self.nombre} ({self.nacionalidad})"


class Libro(Persistent):
    def __init__(self, isbn: str, titulo: str, anio_publicacion: int, categoria: str, num_ejemplares: int):
        super().__init__()
        self.isbn = isbn
        self.titulo = titulo
        self.anio_publicacion = anio_publicacion
        self.categoria = categoria
        self.num_ejemplares = num_ejemplares
        self.disponibles = num_ejemplares
        # Lista persistente para almacenar objetos Autor
        self.autores = PersistentList()

    def agregar_autor(self, autor: Autor):
        self.autores.append(autor)

    def prestar_ejemplar(self) -> bool:
        if self.disponibles > 0:
            self.disponibles -= 1
            self._p_changed = True  # Notifica a ZODB que el objeto cambió
            return True
        return False

    def devolver_ejemplar(self):
        if self.disponibles < self.num_ejemplares:
            self.disponibles += 1
            self._p_changed = True

    def esta_disponible(self) -> bool:
        return self.disponibles > 0


class Prestamo(Persistent):
    def __init__(self, id_prestamo: str, estudiante, libro: Libro, dias_prestamo: int = 7):
        super().__init__()
        self.id_prestamo = id_prestamo
        self.estudiante = estudiante
        self.libro = libro
        self.fecha_prestamo = datetime.date.today()
        self.fecha_limite = self.fecha_prestamo + datetime.timedelta(dias=dias_prestamo)
        self.fecha_devolucion = None
        self.estado = "Activo"

    def registrar_devolucion(self):
        if self.estado == "Activo":
            self.fecha_devolucion = datetime.date.today()
            self.estado = "Devuelto"
            self.libro.devolver_ejemplar()
            self._p_changed = True


class Estudiante(Persistent):
    def __init__(self, matricula: str, nombre: str, carrera: str, email: str):
        super().__init__()
        self.matricula = matricula
        self.nombre = nombre
        self.carrera = carrera
        self.email = email
        # Lista persistente para registrar los préstamos del estudiante
        self.prestamos = PersistentList()

    def agregar_prestamo(self, prestamo: Prestamo):
        self.prestamos.append(prestamo)
        self._p_changed = True

    def obtener_prestamos(self):
        return self.prestamos