"""Entidades del caso. Solo modelan y validan datos; no abren archivos."""
from typing import Optional
from datetime import date
import math
import re

CIUDADES = ("León", "Irapuato", "Celaya", "Salamanca", "Guanajuato Capital")
ESTADOS = ("pendiente", "en_transito", "entregado", "cancelado")


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} debe contener texto.")
    return valor.strip()


def clave(valor, prefijo, digitos):
    valor = texto(valor, "Clave").upper()
    if not re.fullmatch(rf"{prefijo}-[0-9]{{{digitos},}}", valor):
        raise ValueError(f"Clave inválida: se espera {prefijo}-{'0' * digitos}.")
    return valor


def validar_ciudad(valor):
    valor = texto(valor, "Ciudad")
    for nombre in CIUDADES:
        if nombre.casefold() == valor.casefold():
            return nombre
    raise ValueError(f"Ciudad inválida. Opciones: {', '.join(CIUDADES)}.")


def entero_positivo(valor):
    if isinstance(valor, bool) or not re.fullmatch(r"[0-9]+", str(valor).strip()):
        raise ValueError("La cantidad debe ser un número entero positivo.")
    numero = int(valor)
    if numero <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    return numero


def decimal_positivo(valor, campo):
    if isinstance(valor, bool):
        raise ValueError(f"{campo} debe ser un número positivo.")
    try:
        numero = float(valor)
    except (ValueError, TypeError):
        raise ValueError(f"{campo} debe ser un número positivo.") from None
    if not math.isfinite(numero) or numero <= 0:
        raise ValueError(f"{campo} debe ser un número finito mayor que cero.")
    return numero


def fecha_iso(valor):
    valor = texto(valor, "Fecha")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", valor):
        raise ValueError("La fecha debe usar el formato AAAA-MM-DD.")
    try:
        date.fromisoformat(valor)
    except ValueError:
        raise ValueError("La fecha no existe en el calendario.") from None
    return valor


class Cliente:
    """Representa un cliente; no gestiona archivos ni otros clientes."""

    def __init__(self, id_cliente: str, nombre: str, ciudad: str, telefono: str) -> None:
        self.id_cliente = clave(id_cliente, "CLI", 3)
        self.nombre = texto(nombre, "Nombre")
        self.ciudad = validar_ciudad(ciudad)
        self.telefono = texto(telefono, "Teléfono")
        if not re.fullmatch(r"[+0-9 ()-]+", self.telefono) or not 10 <= len(re.sub(r"\D", "", self.telefono)) <= 15:
            raise ValueError("El teléfono debe contener entre 10 y 15 dígitos.")

    def to_dict(self) -> dict:
        """Convierte la entidad en una fila para csv.DictWriter."""
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "ciudad": self.ciudad,
            "telefono": self.telefono,
        }

    @classmethod
    def from_dict(cls, datos: dict):
        """Reconstruye la entidad desde una fila de csv.DictReader."""
        return cls(**datos)

    def __str__(self) -> str:
        """Devuelve una representación legible del registro."""
        return "[" + " - ".join(str(valor) for valor in self.to_dict().values()) + "]"


class Ruta:
    """Representa una ruta fija y su transportista responsable."""

    def __init__(self, id_ruta: str, origen: str, destino: str, distancia_km: float,
                 tiempo_horas: float, transportista: str, disponible: bool = True) -> None:
        self.id_ruta = clave(id_ruta, "RUTA", 2)
        self.origen = validar_ciudad(origen)
        self.destino = validar_ciudad(destino)
        if self.origen == self.destino:
            raise ValueError("El origen y el destino deben ser distintos.")
        self.distancia_km = decimal_positivo(distancia_km, "Distancia")
        self.tiempo_horas = decimal_positivo(tiempo_horas, "Tiempo")
        self.transportista = texto(transportista, "Transportista")
        if isinstance(disponible, str):
            if disponible.lower() not in ("true", "false"):
                raise ValueError("Disponible debe ser True o False.")
            disponible = disponible.lower() == "true"
        if not isinstance(disponible, bool):
            raise ValueError("Disponible debe ser True o False.")
        self.disponible = disponible

    def to_dict(self) -> dict:
        """Convierte la entidad en una fila para csv.DictWriter."""
        return {
            "id_ruta": self.id_ruta,
            "origen": self.origen,
            "destino": self.destino,
            "distancia_km": self.distancia_km,
            "tiempo_horas": self.tiempo_horas,
            "transportista": self.transportista,
            "disponible": self.disponible,
        }

    @classmethod
    def from_dict(cls, datos: dict):
        """Reconstruye la entidad desde una fila de csv.DictReader."""
        return cls(**datos)

    def __str__(self) -> str:
        """Devuelve una representación legible del registro."""
        return "[" + " - ".join(str(valor) for valor in self.to_dict().values()) + "]"


class Pedido:
    """Representa un pedido de traslado de mercancía."""

    def __init__(self, folio: str, id_cliente: str, producto: str, cantidad: int,
                 origen: str, destino: str, fecha: str, estado: str = "pendiente",
                 id_ruta: Optional[str] = None) -> None:
        self.folio = clave(folio, "PED", 4)
        self.id_cliente = clave(id_cliente, "CLI", 3)
        self.producto = texto(producto, "Producto")
        self.cantidad = entero_positivo(cantidad)
        self.origen = validar_ciudad(origen)
        self.destino = validar_ciudad(destino)
        if self.origen == self.destino:
            raise ValueError("El origen y el destino deben ser distintos.")
        self.fecha = fecha_iso(fecha)
        if estado not in ESTADOS:
            raise ValueError("Estado inválido.")
        self.estado = estado
        self.id_ruta = clave(id_ruta, "RUTA", 2) if id_ruta else None
        if estado in ("en_transito", "entregado") and self.id_ruta is None:
            raise ValueError("Un pedido en tránsito o entregado requiere una ruta.")

    def to_dict(self) -> dict:
        """Convierte la entidad en una fila para csv.DictWriter."""
        return {
            "folio": self.folio,
            "id_cliente": self.id_cliente,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "origen": self.origen,
            "destino": self.destino,
            "fecha": self.fecha,
            "estado": self.estado,
            "id_ruta": self.id_ruta,
        }

    @classmethod
    def from_dict(cls, datos: dict):
        """Reconstruye la entidad desde una fila de csv.DictReader."""
        return cls(**datos)

    def __str__(self) -> str:
        """Devuelve una representación legible del registro."""
        return "[" + " - ".join(str(valor) for valor in self.to_dict().values()) + "]"
