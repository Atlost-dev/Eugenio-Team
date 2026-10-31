import pytest


@pytest.mark.parametrize("pasos, destino", [
    pytest.param(["en_transito", "entregado"], "pendiente", id="entregado_a_pendiente"),
    pytest.param(["en_transito"], "cancelado", id="en_transito_a_cancelado"),
    pytest.param([], "entregado", id="pendiente_a_entregado"),
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
