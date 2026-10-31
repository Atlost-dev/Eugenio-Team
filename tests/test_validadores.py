import pytest

from rutas_bajio.modelos import entero_positivo, fecha_iso, validar_ciudad


@pytest.mark.parametrize("entrada, esperado", [
    pytest.param("león", "León", id="minusculas"),
    pytest.param("CELAYA", "Celaya", id="mayusculas"),
])
def test_validar_ciudad_normaliza_mayusculas(entrada, esperado):
    """C-03"""
    assert validar_ciudad(entrada) == esperado


def test_validar_ciudad_fuera_del_catalogo_lanza_value_error():
    """C-03"""
    with pytest.raises(ValueError):
        validar_ciudad("Morelia")


@pytest.mark.parametrize("cantidad", [
    pytest.param(0, id="cero"),
    pytest.param(-5, id="negativo"),
    pytest.param("muchas", id="texto"),
    pytest.param("3.5", id="decimal"),
    pytest.param(True, id="booleano"),
])
def test_entero_positivo_invalido_lanza_value_error(cantidad):
    """C-04"""
    with pytest.raises(ValueError):
        entero_positivo(cantidad)


def test_entero_positivo_convierte_texto_valido():
    """C-04"""
    assert entero_positivo("40") == 40


@pytest.mark.parametrize("fecha", [
    pytest.param("2026-02-30", id="dia_inexistente"),
    pytest.param("15/09/2026", id="formato_incorrecto"),
    pytest.param("", id="vacia"),
])
def test_fecha_iso_invalida_lanza_value_error(fecha):
    """C-07"""
    with pytest.raises(ValueError):
        fecha_iso(fecha)
