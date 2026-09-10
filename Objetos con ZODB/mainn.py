from datetime import datetime
from base_datos import abrir_base_datos, cerrar_base_datos, inicializar_base_datos
from modeloss import Autor, Estudiante, Libro, Prestamo
import transaction


def poblar_base_datos():
  db, connection, root = abrir_base_datos()
  inicializar_base_datos(root)

  print("Poblando la base de datos OODB/ZODB...")

  # ---------------------------------------------------------
  # 1. Crear 10 Autores
  # ---------------------------------------------------------
  autores = [
      Autor(1, "Gabriel García Márquez", "Colombia"),
      Autor(2, "Julio Verne", "Francia"),
      Autor(3, "Jorge Luis Borges", "Argentina"),
      Autor(4, "Isabel Allende", "Chile"),
      Autor(5, "George Orwell", "Reino Unido"),
      Autor(6, "Mario Vargas Llosa", "Perú"),
      Autor(7, "Octavio Paz", "México"),
      Autor(8, "Franz Kafka", "República Checa"),
      Autor(9, "Ray Bradbury", "Estados Unidos"),
      Autor(10, "Virginia Woolf", "Reino Unido"),
  ]
  for autor in autores:
    root.autores[autor.id_autor] = autor

  # ---------------------------------------------------------
  # 2. Crear 10 Libros
  # ---------------------------------------------------------
  libros = [
      Libro("9780307474728", "Cien años de soledad", 1967, "Novela", autores[0]),
      Libro("9780199538474", "Viaje al centro de la Tierra", 1864, "Aventura", autores[1], ),
      Libro("9788420471830", "Ficciones", 1944, "Ficción", autores[2]),
      Libro("9780307474735", "La casa de los espíritus", 1982, "Novela", autores[3], ),
      Libro("9780451524935", "1984", 1949, "Distopía", autores[4]),
      Libro("9788420442570", "La ciudad y los perros", 1963, "Novela", autores[5]),
      Libro("9789681603014", "El laberinto de la soledad", 1950, "Ensayo", autores[6], ),
      Libro("9788420666297", "La metamorfosis", 1915, "Ficción", autores[7]),
      Libro("9781451673319", "Fahrenheit 451", 1953, "Ciencia Ficción", autores[8]),
      Libro("9780156907392", "Al faro", 1927, "Novela", autores[9]),
  ]
  for libro in libros:
    root.libros[libro.isbn] = libro

  # ---------------------------------------------------------
  # 3. Crear 5 Alumnos (Estudiantes)
  # ---------------------------------------------------------
  estudiantes = [Estudiante("A001", "Ana López", "Ingeniería en Sistemas", "ana@universidad.edu.mx", ),
                 Estudiante("A002","Carlos Pérez", "Ingeniería Informática", "carlos@universidad.edu.mx", ),
                 Estudiante("A003", "María Hernández", "Inteligencia Artificial", "maria@universidad.edu.mx", ),
                 Estudiante("A004", "Luis Gómez", "Ciencia de Datos", "luis@universidad.edu.mx", ),
                 Estudiante("A005", "Sofia Ruiz", "Ciberseguridad", "sofia@universidad.edu.mx", )]
  for est in estudiantes:
    root.estudiantes[est.matricula] = est
  # ---------------------------------------------------------
  # 4. Crear 5 Préstamos (3 Activos y 2 Devueltos)
  # ---------------------------------------------------------
  prestamos = [Prestamo(1, root.libros["9780307474728"], root.estudiantes["A001"], datetime(2026, 8, 10), ),
               Prestamo(2, root.libros["9780199538474"], root.estudiantes["A002"], datetime(2026, 8, 12), ),
               Prestamo(3, root.libros["9780451524935"], root.estudiantes["A003"], datetime(2026, 8, 15), ),
               Prestamo(4, root.libros["9788420471830"], root.estudiantes["A004"], datetime(2026, 8, 1), ),
               Prestamo(5, root.libros["9781451673319"], root.estudiantes["A005"], datetime(2026, 8, 5), ),
  ]
  # Registrar devolución en préstamos 4 y 5
  prestamos[3].registrar_devolucion(datetime(2026, 8, 20))
  prestamos[4].registrar_devolucion(datetime(2026, 8, 22))

  for p in prestamos:
    root.prestamos[p.id_prestamo] = p

  transaction.commit()
  print("Base de datos creada y poblada exitosamente.\n")
  cerrar_base_datos(db, connection)


if __name__ == "__main__":
  poblar_base_datos()