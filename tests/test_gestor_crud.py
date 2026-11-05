import pytest

from rutas_bajio.gestor import GestorRutasBajio
from rutas_bajio.modelos import Cliente, Pedido, Ruta


def test_crear_cliente_duplicado_lanza_value_error(gestor, directorio, cliente):
    """C-15"""
    gestor.crear_cliente(cliente)
    antes = (directorio / "clientes.csv").read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        gestor.crear_cliente(Cliente("CLI-010", "Otro", "León", "4771002233"))
    assert (directorio / "clientes.csv").read_text(encoding="utf-8") == antes
    assert len(gestor.clientes) == 1


def test_registrar_pedido_genera_folios_consecutivos(gestor, cliente):
    """C-21"""
    gestor.crear_cliente(cliente)
    assert gestor.ultimo_folio == 0
    p1 = gestor.registrar_pedido("CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15")
    p2 = gestor.registrar_pedido("CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-16")
    assert (p1.folio, p2.folio) == ("PED-0001", "PED-0002")


def test_eliminar_pedido_en_transito_lanza_value_error(gestor_con_datos):
    """C-25"""
    gestor_con_datos.cambiar_estado("PED-0001", "en_transito")
    with pytest.raises(ValueError):
        gestor_con_datos.eliminar_pedido("PED-0001")


def test_eliminar_pedido_inexistente_devuelve_false(gestor_con_datos):
    """C-25"""
    assert gestor_con_datos.eliminar_pedido("PED-9999") is False


def test_pendientes_por_transportista_excluye_cerrados_e_incluye_vacios(gestor_con_datos):
    """C-26"""
    g = gestor_con_datos
    # PED-0001 (RUTA-03, Julián Pérez) queda en tránsito; los demás se cierran
    g.cambiar_estado("PED-0001", "en_transito")
    for folio, estado in [("PED-0002", "entregado"), ("PED-0003", "cancelado")]:
        g.crear_pedido(Pedido(folio, "CLI-010", "Acero", 1, "León", "Irapuato", "2026-09-15",
                              id_ruta="RUTA-01"))
        if estado == "entregado":
            g.cambiar_estado(folio, "en_transito")
        g.cambiar_estado(folio, estado)
    g.crear_pedido(Pedido("PED-0004", "CLI-010", "Acero", 1, "León", "Irapuato", "2026-09-15",
                          id_ruta="RUTA-01"))
    g.crear_ruta(Ruta("RUTA-04", "Celaya", "León", 95, 2, "Sin Pedidos"))

    resultado = g.pendientes_por_transportista()
    assert [p.folio for p in resultado["Julián Pérez"]] == ["PED-0001"]
    assert [p.folio for p in resultado["Miguel Ángel Torres"]] == ["PED-0004"]
    assert resultado["Sin Pedidos"] == []


def test_rutas_compatibles_solo_disponibles_del_mismo_trayecto(gestor_con_datos):
    """C-27"""
    gestor_con_datos.crear_ruta(Ruta("RUTA-04", "León", "Guanajuato Capital", 60, 1.6,
                                     "Otro", disponible=False))
    gestor_con_datos.crear_ruta(Ruta("RUTA-05", "Celaya", "León", 95, 2, "Otro"))
    # PED-0001 es León -> Guanajuato Capital: solo RUTA-03 es disponible y coincide
    assert [r.id_ruta for r in gestor_con_datos.rutas_compatibles("PED-0001")] == ["RUTA-03"]


@pytest.mark.parametrize("estado, id_ruta", [
    pytest.param("cancelado", None, id="nace_cancelado"),
    pytest.param("entregado", "RUTA-03", id="nace_entregado"),
])
def test_crear_pedido_estado_inicial_no_pendiente_lanza_value_error(gestor_con_datos, estado, id_ruta):
    """C-32"""
    pedido = Pedido("PED-0002", "CLI-010", "Acero", 5, "León", "Guanajuato Capital", "2026-09-15",
                    estado=estado, id_ruta=id_ruta)
    with pytest.raises(ValueError, match="debe estar pendiente"):
        gestor_con_datos.crear_pedido(pedido)
    assert gestor_con_datos.buscar_pedido("PED-0002") is None


def test_actualizar_ruta_con_pedidos_no_cambia_trayecto(gestor_con_datos, directorio):
    """C-34"""
    with pytest.raises(ValueError, match="trayecto"):
        gestor_con_datos.actualizar_ruta("RUTA-03", destino="Irapuato")
    recargado = GestorRutasBajio(str(directorio))
    assert recargado.buscar_ruta("RUTA-03").destino == "Guanajuato Capital"
