import pytest


@pytest.mark.parametrize("pasos, destino", [
    pytest.param(["en_transito", "entregado"], "pendiente", id="entregado_a_pendiente"),
    pytest.param(["en_transito"], "cancelado", id="en_transito_a_cancelado"),
    pytest.param([], "entregado", id="pendiente_a_entregado"),
    pytest.param(["en_transito"], "pendiente", id="en_transito_a_pendiente"),
    pytest.param([], "pendiente", id="pendiente_a_pendiente"),
])
def test_cambiar_estado_prohibido_lanza_value_error(gestor_con_datos, pasos, destino):
    """C-24"""
    for paso in pasos:
        gestor_con_datos.cambiar_estado("PED-0001", paso)
    actual = gestor_con_datos.buscar_pedido("PED-0001").estado
    with pytest.raises(ValueError, match="Cambio no permitido"):
        gestor_con_datos.cambiar_estado("PED-0001", destino)
    assert gestor_con_datos.buscar_pedido("PED-0001").estado == actual


def test_cancelar_pedido_en_transito_lanza_value_error(gestor_con_datos):
    """C-24"""
    gestor_con_datos.cambiar_estado("PED-0001", "en_transito")
    with pytest.raises(ValueError, match="Cambio no permitido"):
        gestor_con_datos.cancelar_pedido("PED-0001")


def test_cancelar_pedido_pendiente_es_valido(gestor_con_datos):
    """C-28"""
    assert gestor_con_datos.cancelar_pedido("PED-0001") is True
    assert gestor_con_datos.buscar_pedido("PED-0001").estado == "cancelado"


@pytest.mark.parametrize("final, pasos", [
    pytest.param("entregado", ["en_transito", "entregado"], id="entregado"),
    pytest.param("cancelado", ["cancelado"], id="cancelado"),
])
@pytest.mark.parametrize("destino", ["pendiente", "en_transito", "entregado", "cancelado"])
def test_estado_final_no_tiene_salidas(gestor_con_datos, final, pasos, destino):
    """C-29"""
    for paso in pasos:
        gestor_con_datos.cambiar_estado("PED-0001", paso)
    with pytest.raises(ValueError, match="Cambio no permitido"):
        gestor_con_datos.cambiar_estado("PED-0001", destino)
    assert gestor_con_datos.buscar_pedido("PED-0001").estado == final


def test_pedido_sin_ruta_no_sale_a_transito(gestor_con_datos):
    """C-30"""
    pedido = gestor_con_datos.registrar_pedido("CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15")
    with pytest.raises(ValueError, match="requiere una ruta"):
        gestor_con_datos.cambiar_estado(pedido.folio, "en_transito")
    assert gestor_con_datos.buscar_pedido(pedido.folio).estado == "pendiente"


def test_cambiar_estado_inexistente_lanza_value_error(gestor_con_datos):
    """C-31"""
    with pytest.raises(ValueError):
        gestor_con_datos.cambiar_estado("PED-0001", "perdido")
    assert gestor_con_datos.buscar_pedido("PED-0001").estado == "pendiente"


def test_cambiar_estado_folio_inexistente_devuelve_false(gestor_con_datos):
    """C-31"""
    assert gestor_con_datos.cambiar_estado("PED-9999", "en_transito") is False
