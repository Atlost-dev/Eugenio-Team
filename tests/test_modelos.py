import pytest

from rutas_bajio.modelos import Cliente, Pedido, Ruta


def _cliente(id_cliente="CLI-010", telefono="4731002233"):
    return Cliente(id_cliente, "Constructora Guanajuato", "Guanajuato Capital", telefono)


@pytest.mark.parametrize("id_cliente", [
    pytest.param("CLI-1", id="pocos_digitos"),
    pytest.param("", id="vacia"),
    pytest.param("PED-0001", id="prefijo_ajeno"),
    pytest.param("cli", id="sin_numero"),
])
def test_cliente_clave_mal_formada_lanza_value_error(id_cliente):
    """C-01"""
    with pytest.raises(ValueError):
        _cliente(id_cliente=id_cliente)


@pytest.mark.parametrize("digitos, valido", [
    pytest.param(9, False, id="telefono_9_digitos"),
    pytest.param(10, True, id="telefono_10_digitos"),
    pytest.param(15, True, id="telefono_15_digitos"),
    pytest.param(16, False, id="telefono_16_digitos"),
])
def test_cliente_telefono_limites(digitos, valido):
    """C-02"""
    telefono = "1" * digitos
    if valido:
        assert _cliente(telefono=telefono).telefono == telefono
    else:
        with pytest.raises(ValueError):
            _cliente(telefono=telefono)


def test_ruta_origen_igual_destino_lanza_value_error():
    """C-05"""
    with pytest.raises(ValueError):
        Ruta("RUTA-01", "León", "León", 10, 1, "Miguel")


def test_pedido_origen_igual_destino_lanza_value_error():
    """C-05"""
    with pytest.raises(ValueError):
        Pedido("PED-0001", "CLI-010", "Acero", 1, "León", "León", "2026-09-15")


def test_pedido_en_transito_sin_ruta_lanza_value_error():
    """C-06"""
    with pytest.raises(ValueError):
        Pedido("PED-0001", "CLI-010", "Acero", 1, "León", "Irapuato", "2026-09-15",
               estado="en_transito", id_ruta=None)


@pytest.mark.parametrize("entidad", [
    pytest.param(Pedido("PED-0001", "CLI-010", "Acero", 5, "León", "Irapuato", "2026-09-15"),
                 id="pedido_sin_ruta"),
    pytest.param(Pedido("PED-0002", "CLI-010", "Acero", 5, "León", "Guanajuato Capital",
                        "2026-09-15", id_ruta="RUTA-03"), id="pedido_con_ruta"),
    pytest.param(Ruta("RUTA-03", "León", "Guanajuato Capital", 55, 1.5, "Julián", disponible=False),
                 id="ruta_no_disponible"),
])
def test_to_dict_from_dict_ida_y_vuelta(entidad):
    """C-08"""
    copia = type(entidad).from_dict(entidad.to_dict())
    assert copia.to_dict() == entidad.to_dict()
