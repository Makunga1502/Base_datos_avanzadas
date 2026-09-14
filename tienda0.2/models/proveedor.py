"""Modelo que representa a un proveedor del sistema."""

from persistent import Persistent


class Proveedor(Persistent):
    """Representa a una entidad física o moral que surte mercancía a la tienda."""

    def __init__(
        self,
        id_proveedor: str,
        rfc: str,
        razon_social: str,
        telefono: str,
        email: str,
    ) -> None:
        super().__init__()
        self.id_proveedor = id_proveedor
        self.rfc = rfc
        self.razon_social = razon_social
        self.telefono = telefono
        self.email = email

    def __repr__(self) -> str:
        return f"<Proveedor: {self.razon_social} (RFC: {self.rfc})>"