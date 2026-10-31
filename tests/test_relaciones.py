import pytest

from rutas_bajio.gestor import GestorRutasBajio
from rutas_bajio.modelos import Pedido


def test_crear_pedido_cliente_inexistente_lanza_value_error(gestor, directorio):
    """C-16"""
    with pytest.raises(ValueError, match="cliente"):
        gestor.crear_pedido(Pedido("PED-0001", "CLI-404", "Acero", 5, "León", "Irapuato", "2026-09-15"))
    assert gestor.pedidos == []
    assert not (directorio / "pedidos.csv").exists()


def test_crear_pedido_ruta_de_otro_trayecto_lanza_value_error(gestor_con_datos):
    """C-17"""
    pedido = Pedido("PED-0002", "CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15", id_ruta="RUTA-03")
    with pytest.raises(ValueError):
        gestor_con_datos.crear_pedido(pedido)
    assert gestor_con_datos.buscar_pedido("PED-0002") is None


def test_asignar_ruta_de_otro_trayecto_lanza_value_error(gestor_con_datos):
    """C-17"""
    with pytest.raises(ValueError):
        gestor_con_datos.asignar_ruta("PED-0001", "RUTA-01")
    assert gestor_con_datos.buscar_pedido("PED-0001").id_ruta == "RUTA-03"


def test_crear_pedido_ruta_no_disponible_lanza_value_error(gestor_con_datos):
    """C-18"""
    pedido = Pedido("PED-0002", "CLI-010", "Acero", 5, "León", "Celaya", "2026-09-15", id_ruta="RUTA-02")
    with pytest.raises(ValueError, match="no está disponible"):
        gestor_con_datos.crear_pedido(pedido)


@pytest.mark.parametrize("eliminar, identificador", [
    pytest.param("eliminar_cliente", "CLI-010", id="cliente_con_pedidos"),
    pytest.param("eliminar_ruta", "RUTA-03", id="ruta_con_pedidos"),
])
def test_eliminar_con_pedidos_asociados_lanza_value_error(gestor_con_datos, directorio, eliminar, identificador):
    """C-20"""
    with pytest.raises(ValueError):
        getattr(gestor_con_datos, eliminar)(identificador)
    recargado = GestorRutasBajio(str(directorio))
    assert (recargado.buscar_cliente("CLI-010") and recargado.buscar_ruta("RUTA-03"))
