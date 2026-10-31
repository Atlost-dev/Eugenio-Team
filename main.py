"""Punto de entrada. Ejecutar: py main.py."""
import argparse
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from rutas_bajio import Cliente, Ruta, GestorRutasBajio
from rutas_bajio.consola import ejecutar_menu


def demo():
    with TemporaryDirectory(prefix="rutas_bajio_") as directorio:
        gestor = GestorRutasBajio(directorio)
        gestor.crear_cliente(Cliente("CLI-010", "Constructora Guanajuato S.A.", "Guanajuato Capital", "473-100-2233"))
        gestor.crear_ruta(Ruta("RUTA-03", "León", "Guanajuato Capital", 55, 1.5, "Julián Pérez"))
        pedido = gestor.crear_pedido("CLI-010", "Láminas de acero calibre 20", 40,
                                    "León", "Guanajuato Capital", "2026-09-15")
        print("Creado:", pedido)
        gestor.asignar_ruta(pedido.folio, "RUTA-03")
        gestor.cambiar_estado(pedido.folio, "en_transito")
        print("Seguimiento:", gestor.detalle_pedido(pedido.folio))
        gestor.cambiar_estado(pedido.folio, "entregado")
        recargado = GestorRutasBajio(directorio)
        assert recargado.buscar_pedido(pedido.folio).estado == "entregado"
        try:
            recargado.cambiar_estado(pedido.folio, "pendiente")
        except ValueError as error:
            print("Protección de estado:", error)
        print("Demostración completada; persistencia y cierre comprobados.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CRUD de logística con persistencia CSV.")
    parser.add_argument("--datos", type=Path, default=Path(__file__).resolve().parent / "datos")
    parser.add_argument("--demo", action="store_true", help="Demostración en archivos temporales.")
    args = parser.parse_args()
    try:
        if args.demo:
            demo()
        else:
            ejecutar_menu(args.datos)
    except (ValueError, OSError, csv.Error) as error:
        parser.exit(1, f"No se pudo abrir el sistema: {error}\n")
    except (EOFError, KeyboardInterrupt):
        print("\nSesión terminada.")
