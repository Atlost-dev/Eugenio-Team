import pytest

from rutas_bajio.gestor import GestorRutasBajio
from rutas_bajio.modelos import Pedido, Ruta

pytestmark = pytest.mark.integracion


def test_crear_y_recargar_conserva_registros_y_orden(gestor, directorio, cliente):
    """C-11"""
    gestor.crear_cliente(cliente)
    gestor.crear_ruta(Ruta("RUTA-01", "León", "Irapuato", 30, 0.6, "Miguel"))
    for folio in ("PED-0001", "PED-0002"):
        gestor.crear_pedido(Pedido(folio, "CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15"))

    otro = GestorRutasBajio(str(directorio))
    for atributo in ("clientes", "rutas", "pedidos"):
        assert [r.to_dict() for r in getattr(otro, atributo)] == \
               [r.to_dict() for r in getattr(gestor, atributo)]
    assert [p.folio for p in otro.pedidos] == ["PED-0001", "PED-0002"]


def test_folio_no_se_reutiliza_tras_eliminar_pedido(gestor, directorio, cliente):
    """C-22"""
    gestor.crear_cliente(cliente)
    primero = gestor.registrar_pedido("CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15")
    assert primero.folio == "PED-0001"
    gestor.eliminar_pedido("PED-0001")

    recargado = GestorRutasBajio(str(directorio))
    assert recargado.ultimo_folio == 1
    assert recargado.registrar_pedido("CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15").folio == "PED-0002"


def test_cambiar_estado_flujo_valido_persiste(gestor_con_datos, directorio):
    """C-23"""
    for estado in ("en_transito", "entregado"):
        assert gestor_con_datos.cambiar_estado("PED-0001", estado) is True
        assert GestorRutasBajio(str(directorio)).buscar_pedido("PED-0001").estado == estado
