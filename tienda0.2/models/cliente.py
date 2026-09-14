"""Modelo que representa a un cliente del sistema."""

from persistent import Persistent


class Cliente(Persistent):
    """Representa a un comprador registrado dentro del sistema."""

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        telefono: str,
        email: str,
        direccion: str,
    ) -> None:
        super().__init__()
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion

    def __repr__(self) -> str:
        return f"<Cliente: {self.nombre} (ID: {self.id_cliente})>"