"""Gestor con persistencia en CSV (código copiado sin cambios de Desarrollo.ipynb)."""
import csv
from pathlib import Path
from typing import Optional

from .modelos import Cliente, Ruta, Pedido, ESTADOS, clave


class GestorRutasBajio:
    CAMPOS_CLIENTES = ["id_cliente", "nombre", "ciudad", "telefono"]
    CAMPOS_RUTAS = ["id_ruta", "origen", "destino", "distancia_km", "tiempo_horas", "transportista", "disponible"]
    CAMPOS_PEDIDOS = ["folio", "id_cliente", "producto", "cantidad", "origen", "destino", "fecha", "estado", "id_ruta"]

    def __init__(self, directorio: str = "datos_notebook") -> None:
        self.directorio = Path(directorio)
        self.clientes = []
        self.rutas = []
        self.pedidos = []
        self.ultimo_folio = 0
        self.cargar()

    def _leer(self, nombre, campos, clase) -> list:
        try:
            with open(self.directorio / nombre, "r", newline="", encoding="utf-8-sig") as archivo:
                lector = csv.DictReader(archivo, strict=True)
                if lector.fieldnames != campos:
                    raise ValueError(f"Encabezados incorrectos en {nombre}.")
                registros = []
                for numero, fila in enumerate(lector, 2):
                    if None in fila or any(valor is None for valor in fila.values()):
                        raise ValueError(f"Fila incompleta en {nombre}, fila {numero}.")
                    try:
                        registros.append(clase.from_dict(fila))
                    except (ValueError, TypeError) as error:
                        raise ValueError(f"{nombre}, fila {numero}: {error}") from error
                return registros
        except FileNotFoundError:
            return []

    def _escribir(self, nombre, campos, filas) -> None:
        self.directorio.mkdir(parents=True, exist_ok=True)
        ruta = self.directorio / nombre
        temporal = ruta.with_suffix(".tmp")
        try:
            with open(temporal, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(filas)
            temporal.replace(ruta)
        finally:
            if temporal.exists():
                temporal.unlink()

    def cargar(self) -> None:
        clientes = self._leer("clientes.csv", self.CAMPOS_CLIENTES, Cliente)
        rutas = self._leer("rutas.csv", self.CAMPOS_RUTAS, Ruta)
        pedidos = self._leer("pedidos.csv", self.CAMPOS_PEDIDOS, Pedido)
        for registros, atributo in [(clientes, "id_cliente"), (rutas, "id_ruta"), (pedidos, "folio")]:
            claves = [getattr(registro, atributo) for registro in registros]
            if len(claves) != len(set(claves)):
                raise ValueError("Hay claves duplicadas en los archivos CSV.")
        for pedido in pedidos:
            if not any(c.id_cliente == pedido.id_cliente for c in clientes):
                raise ValueError(f"El cliente de {pedido.folio} no existe.")
            if pedido.id_ruta:
                ruta = next((r for r in rutas if r.id_ruta == pedido.id_ruta), None)
                if ruta is None or (pedido.origen, pedido.destino) != (ruta.origen, ruta.destino):
                    raise ValueError(f"La ruta de {pedido.folio} no existe o no coincide con su trayecto.")
        ultimo = max((int(p.folio.split("-")[1]) for p in pedidos), default=0)
        try:
            with open(self.directorio / "secuencias.csv", "r", newline="", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                filas = list(lector)
                if lector.fieldnames != ["ultimo_folio"] or len(filas) != 1 or not (filas[0].get("ultimo_folio") or "").isdigit():
                    raise ValueError("El archivo de consecutivos es incorrecto.")
                ultimo = max(ultimo, int(filas[0]["ultimo_folio"]))
        except FileNotFoundError:
            pass
        self.clientes, self.rutas, self.pedidos = clientes, rutas, pedidos
        self.ultimo_folio = ultimo

    def guardar(self) -> None:
        self._escribir("clientes.csv", self.CAMPOS_CLIENTES, [c.to_dict() for c in self.clientes])
        self._escribir("rutas.csv", self.CAMPOS_RUTAS, [r.to_dict() for r in self.rutas])
        self._escribir("secuencias.csv", ["ultimo_folio"], [{"ultimo_folio": self.ultimo_folio}])
        self._escribir("pedidos.csv", self.CAMPOS_PEDIDOS, [p.to_dict() for p in self.pedidos])

    def _guardar_lista(self, entidad, registros) -> None:
        campos = {"clientes": self.CAMPOS_CLIENTES, "rutas": self.CAMPOS_RUTAS, "pedidos": self.CAMPOS_PEDIDOS}
        self._escribir(entidad + ".csv", campos[entidad], [r.to_dict() for r in registros])
        setattr(self, entidad, registros)


class GestorRutasBajio(GestorRutasBajio):
    def buscar_cliente(self, id_cliente: str) -> Optional[Cliente]:
        identificador = clave(id_cliente, "CLI", 3)
        for cliente in self.clientes:
            if cliente.id_cliente == identificador:
                return cliente
        return None

    def buscar_ruta(self, id_ruta: str) -> Optional[Ruta]:
        identificador = clave(id_ruta, "RUTA", 2)
        for ruta in self.rutas:
            if ruta.id_ruta == identificador:
                return ruta
        return None

    def buscar_pedido(self, folio: str) -> Optional[Pedido]:
        identificador = clave(folio, "PED", 4)
        for pedido in self.pedidos:
            if pedido.folio == identificador:
                return pedido
        return None

    def crear_cliente(self, cliente: Cliente) -> None:
        if self.buscar_cliente(cliente.id_cliente):
            raise ValueError(f"Ya existe el cliente {cliente.id_cliente}.")
        self._guardar_lista("clientes", self.clientes + [cliente])

    def crear_ruta(self, ruta: Ruta) -> None:
        if self.buscar_ruta(ruta.id_ruta):
            raise ValueError(f"Ya existe la ruta {ruta.id_ruta}.")
        self._guardar_lista("rutas", self.rutas + [ruta])

    def _validar_relaciones(self, pedido: Pedido, disponible: bool = False) -> None:
        if self.buscar_cliente(pedido.id_cliente) is None:
            raise ValueError("El cliente del pedido no existe.")
        if pedido.id_ruta:
            ruta = self.buscar_ruta(pedido.id_ruta)
            if ruta is None:
                raise ValueError("La ruta del pedido no existe.")
            if (pedido.origen, pedido.destino) != (ruta.origen, ruta.destino):
                raise ValueError("La ruta no coincide con el origen y destino del pedido.")
            if disponible and not ruta.disponible:
                raise ValueError("La ruta no está disponible.")

    def crear_pedido(self, pedido: Pedido) -> None:
        if self.buscar_pedido(pedido.folio):
            raise ValueError(f"Ya existe el pedido {pedido.folio}.")
        if pedido.estado != "pendiente":
            raise ValueError("Un pedido nuevo debe estar pendiente.")
        self._validar_relaciones(pedido, disponible=True)
        ultimo = max(self.ultimo_folio, int(pedido.folio.split("-")[1]))
        self._escribir("secuencias.csv", ["ultimo_folio"], [{"ultimo_folio": ultimo}])
        self.ultimo_folio = ultimo
        self._guardar_lista("pedidos", self.pedidos + [pedido])

    def registrar_pedido(self, id_cliente: str, producto: str, cantidad: int, origen: str,
                         destino: str, fecha: str, id_ruta: Optional[str] = None) -> Pedido:
        """Genera el siguiente folio automáticamente para las nuevas solicitudes."""
        pedido = Pedido(f"PED-{self.ultimo_folio + 1:04d}", id_cliente, producto, cantidad,
                        origen, destino, fecha, id_ruta=id_ruta)
        self.crear_pedido(pedido)
        return pedido


class GestorRutasBajio(GestorRutasBajio):
    """Extiende el gestor con las operaciones READ del CRUD."""

    def listar_clientes(self) -> list:
        return list(self.clientes)

    def listar_rutas(self) -> list:
        return list(self.rutas)

    def listar_pedidos(self, estado: Optional[str] = None) -> list:
        if estado is not None and estado not in ESTADOS:
            raise ValueError("Estado de consulta inválido.")
        return [p for p in self.pedidos if estado is None or p.estado == estado]

    def pedidos_por_cliente(self, id_cliente: str) -> list:
        cliente = self.buscar_cliente(id_cliente)
        if cliente is None:
            raise ValueError("El cliente no existe.")
        return [p for p in self.pedidos if p.id_cliente == cliente.id_cliente]

    def pendientes_por_transportista(self, transportista: Optional[str] = None) -> dict:
        """Pendientes de entregar: pendientes asignados y en tránsito."""
        resultado = {}
        for ruta in self.rutas:
            if transportista is None or ruta.transportista.casefold() == transportista.strip().casefold():
                resultado.setdefault(ruta.transportista, [])
        for pedido in self.pedidos:
            if pedido.id_ruta and pedido.estado in ("pendiente", "en_transito"):
                nombre = self.buscar_ruta(pedido.id_ruta).transportista
                if nombre in resultado:
                    resultado[nombre].append(pedido)
        return resultado

    def pedidos_sin_ruta(self) -> list:
        return [p for p in self.pedidos if p.estado == "pendiente" and p.id_ruta is None]

    def rutas_compatibles(self, folio: str) -> list:
        pedido = self.buscar_pedido(folio)
        if pedido is None:
            raise ValueError("El pedido no existe.")
        return [r for r in self.rutas if r.disponible and (r.origen, r.destino) == (pedido.origen, pedido.destino)]

    def detalle_pedido(self, folio: str) -> dict:
        pedido = self.buscar_pedido(folio)
        if pedido is None:
            raise ValueError("El pedido no existe.")
        cliente = self.buscar_cliente(pedido.id_cliente)
        ruta = self.buscar_ruta(pedido.id_ruta) if pedido.id_ruta else None
        return {**pedido.to_dict(), "cliente": cliente.nombre, "transportista": ruta.transportista if ruta else None}


class GestorRutasBajio(GestorRutasBajio):
    """Extiende el gestor con la operación UPDATE del CRUD."""

    def actualizar_cliente(self, id_cliente: str, /, **cambios) -> bool:
        cliente = self.buscar_cliente(id_cliente)
        if cliente is None:
            return False
        if set(cambios) - {"nombre", "ciudad", "telefono"}:
            raise ValueError("No se cambia la clave ni se agregan atributos desconocidos.")
        nuevo = Cliente.from_dict({**cliente.to_dict(), **cambios})
        self._guardar_lista("clientes", [nuevo if c.id_cliente == cliente.id_cliente else c for c in self.clientes])
        return True

    def actualizar_ruta(self, id_ruta: str, /, **cambios) -> bool:
        ruta = self.buscar_ruta(id_ruta)
        if ruta is None:
            return False
        if set(cambios) - {"origen", "destino", "distancia_km", "tiempo_horas", "transportista", "disponible"}:
            raise ValueError("No se cambia la clave ni se agregan atributos desconocidos.")
        nueva = Ruta.from_dict({**ruta.to_dict(), **cambios})
        for pedido in self.pedidos:
            if pedido.id_ruta == ruta.id_ruta:
                if (pedido.origen, pedido.destino) != (nueva.origen, nueva.destino):
                    raise ValueError("El trayecto no coincide con los pedidos asociados.")
                if pedido.estado != "pendiente" and any(getattr(ruta, c) != getattr(nueva, c)
                    for c in ("origen", "destino", "distancia_km", "tiempo_horas", "transportista")):
                    raise ValueError("Una ruta con pedidos en tránsito o cerrados solo cambia su disponibilidad.")
        self._guardar_lista("rutas", [nueva if r.id_ruta == ruta.id_ruta else r for r in self.rutas])
        return True

    def actualizar_pedido(self, folio: str, /, **cambios) -> bool:
        """Corrige un pedido pendiente; devuelve False si no se encuentra."""
        pedido = self.buscar_pedido(folio)
        if pedido is None:
            return False
        if pedido.estado != "pendiente":
            raise ValueError("Solo se corrigen datos de pedidos pendientes.")
        if set(cambios) - {"id_cliente", "producto", "cantidad", "origen", "destino", "fecha", "id_ruta"}:
            raise ValueError("No se cambia el folio; usa cambiar_estado para cambiar la situación.")
        nuevo = Pedido.from_dict({**pedido.to_dict(), **cambios})
        self._validar_relaciones(nuevo, disponible=True)
        self._guardar_lista("pedidos", [nuevo if p.folio == pedido.folio else p for p in self.pedidos])
        return True

    def asignar_ruta(self, folio: str, id_ruta: Optional[str]) -> bool:
        return self.actualizar_pedido(folio, id_ruta=id_ruta)

    def cambiar_estado(self, folio: str, estado: str) -> bool:
        pedido = self.buscar_pedido(folio)
        if pedido is None:
            return False
        transiciones = {"pendiente": ("en_transito", "cancelado"), "en_transito": ("entregado",),
                        "entregado": (), "cancelado": ()}
        if estado not in transiciones[pedido.estado]:
            raise ValueError(f"Cambio no permitido: {pedido.estado} -> {estado}.")
        nuevo = Pedido.from_dict({**pedido.to_dict(), "estado": estado})
        self._validar_relaciones(nuevo, disponible=estado == "en_transito")
        self._guardar_lista("pedidos", [nuevo if p.folio == pedido.folio else p for p in self.pedidos])
        return True

    def cancelar_pedido(self, folio: str) -> bool:
        return self.cambiar_estado(folio, "cancelado")


class GestorRutasBajio(GestorRutasBajio):
    """Extiende el gestor con la operación DELETE del CRUD."""

    def eliminar_cliente(self, id_cliente: str) -> bool:
        cliente = self.buscar_cliente(id_cliente)
        if cliente is None:
            return False
        if any(p.id_cliente == cliente.id_cliente for p in self.pedidos):
            raise ValueError("No se elimina un cliente con pedidos asociados.")
        self._guardar_lista("clientes", [c for c in self.clientes if c.id_cliente != cliente.id_cliente])
        return True

    def eliminar_ruta(self, id_ruta: str) -> bool:
        ruta = self.buscar_ruta(id_ruta)
        if ruta is None:
            return False
        if any(p.id_ruta == ruta.id_ruta for p in self.pedidos):
            raise ValueError("No se elimina una ruta con pedidos asociados.")
        self._guardar_lista("rutas", [r for r in self.rutas if r.id_ruta != ruta.id_ruta])
        return True

    def eliminar_pedido(self, folio: str) -> bool:
        pedido = self.buscar_pedido(folio)
        if pedido is None:
            return False
        if pedido.estado not in ("pendiente", "cancelado"):
            raise ValueError("Solo se dan de baja pedidos pendientes o cancelados.")
        self._escribir("secuencias.csv", ["ultimo_folio"], [{"ultimo_folio": self.ultimo_folio}])
        self._guardar_lista("pedidos", [p for p in self.pedidos if p.folio != pedido.folio])
        return True
