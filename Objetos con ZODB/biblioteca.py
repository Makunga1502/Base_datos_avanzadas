from base_datos import abrir_base_datos, cerrar_base_datos, inicializar_base_datos


def mostrar_registro_prestamo(id_prestamo):
  db, connection, root = abrir_base_datos()
  inicializar_base_datos(
      root
  )  # Asegura que root.prestamos exista en el esquema

  print("\nREGISTRO DE PRÉSTAMO")

  # Acceso directo al diccionario persistente de préstamos
  if hasattr(root, "prestamos"):
    prestamo = root.prestamos.get(id_prestamo)

    if prestamo:
      print(f"ID Préstamo : {prestamo.id_prestamo}")
      print(f"Alumno      : {prestamo.estudiante.nombre}")
      print(f"Título Libro: {prestamo.libro.titulo}")
      print(f"Estado      : {prestamo.estado}")
    else:
      print(f"No se encontró el préstamo con ID: {id_prestamo}")
  else:
    print("La colección de préstamos no está inicializada.")

  cerrar_base_datos(db, connection)


def mostrar_prestamos_por_alumno(matricula):
  db, connection, root = abrir_base_datos()
  inicializar_base_datos(root)

  estudiante = root.estudiantes.get(matricula)

  print(f"\nPRÉSTAMOS DEL ALUMNO ({matricula})")
  if estudiante:
    print(f"Estudiante: {estudiante.nombre}")
    encontrados = False
    for p in root.prestamos.values():
      if p.estudiante.matricula == matricula:
        print(
            f"  - Préstamo #{p.id_prestamo}: '{p.libro.titulo}' | Estado:"
            f" {p.estado}"
        )
        encontrados = True
    if not encontrados:
      print("No tiene préstamos registrados.")
  else:
    print("Estudiante no registrado.")

  cerrar_base_datos(db, connection)


def mostrar_libros_prestados():
  db, connection, root = abrir_base_datos()
  inicializar_base_datos(root)

  print("\n--- LIBROS ACTUALMENTE PRESTADOS ---")

  libros_prestados = [
      l for l in root.libros.values() if not l.esta_disponible()
  ]

  if libros_prestados:
    for libro in libros_prestados:
      print(f"ISBN: {libro.isbn} | Título: {libro.titulo}")
  else:
    print("No hay libros prestados en este momento.")

  cerrar_base_datos(db, connection)


def generar_reporte():
  db, connection, root = abrir_base_datos()
  inicializar_base_datos(root)

  total_libros = len(root.libros)
  disponibles = sum(1 for l in root.libros.values() if l.esta_disponible())
  prestados = total_libros - disponibles

  total_estudiantes = len(root.estudiantes)
  total_autores = len(root.autores)

  total_prestamos = len(root.prestamos)
  activos = sum(1 for p in root.prestamos.values() if p.esta_activo())
  devueltos = total_prestamos - activos

  print("REPORTE DE BIBLIOTECA")
  
  print("LIBROS")
  print("-" * 40)
  print(f"Total de libros: {total_libros}")
  print(f"Disponibles: {disponibles}")
  print(f"Prestados: {prestados}")
  print("ESTUDIANTES")
  print("-" * 40)
  print(f"Total de estudiantes: {total_estudiantes}")
  print("AUTORES")
  print("-" * 40)
  print(f"Total de autores: {total_autores}")
  print("PRÉSTAMOS")
  print("-" * 40)
  print(f"Total de préstamos: {total_prestamos}")
  print(f"Activos: {activos}")
  print(f"Devueltos: {devueltos}")

  cerrar_base_datos(db, connection)


if __name__ == "__main__":
  mostrar_registro_prestamo(1)
  mostrar_prestamos_por_alumno("A001")
  mostrar_libros_prestados()
  generar_reporte()