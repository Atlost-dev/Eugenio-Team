import pytest

from rutas_bajio.gestor import GestorRutasBajio
from rutas_bajio.modelos import Cliente

pytestmark = pytest.mark.csv

ENCABEZADO_CLIENTES = "id_cliente,nombre,ciudad,telefono\n"


def test_cargar_sin_archivos_arranca_vacio(gestor):
    """C-09"""
    assert (gestor.clientes, gestor.rutas, gestor.pedidos) == ([], [], [])
    assert gestor.ultimo_folio == 0


def test_cargar_csv_solo_encabezado_equivale_a_vacio(directorio):
    """C-10"""
    directorio.mkdir()
    (directorio / "clientes.csv").write_text(ENCABEZADO_CLIENTES, encoding="utf-8")
    assert GestorRutasBajio(str(directorio)).clientes == []


def test_leer_encabezados_incorrectos_lanza_value_error(directorio):
    """C-12"""
    directorio.mkdir()
    (directorio / "clientes.csv").write_text("id,nombre\nCLI-010,Ana\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Encabezados incorrectos"):
        GestorRutasBajio(str(directorio))


def test_leer_fila_incompleta_lanza_value_error(directorio):
    """C-12"""
    directorio.mkdir()
    (directorio / "clientes.csv").write_text(ENCABEZADO_CLIENTES + "CLI-010,Ana\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Fila incompleta"):
        GestorRutasBajio(str(directorio))


def test_guardar_conserva_comas_y_acentos(gestor, directorio):
    """C-13"""
    nombre = "Aceros, Fundición del Bajío"
    gestor.crear_cliente(Cliente("CLI-010", nombre, "León", "4771002233"))
    recargado = GestorRutasBajio(str(directorio))
    assert recargado.buscar_cliente("CLI-010").nombre == nombre
    assert recargado.buscar_cliente("CLI-010").ciudad == "León"


def test_escribir_no_deja_archivos_tmp(gestor, directorio, cliente):
    """C-14"""
    gestor.crear_cliente(cliente)
    assert list(directorio.glob("*.tmp")) == []


def test_cargar_pedido_con_cliente_inexistente_lanza_value_error(directorio):
    """C-19"""
    directorio.mkdir()
    (directorio / "pedidos.csv").write_text(
        "folio,id_cliente,producto,cantidad,origen,destino,fecha,estado,id_ruta\n"
        "PED-0001,CLI-099,Acero,5,León,Irapuato,2026-09-15,pendiente,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="El cliente de PED-0001 no existe"):
        GestorRutasBajio(str(directorio))


def test_cargar_claves_duplicadas_en_csv_lanza_value_error(directorio):
    """C-33"""
    directorio.mkdir()
    fila = "CLI-010,Ana,León,4771002233\n"
    (directorio / "clientes.csv").write_text(ENCABEZADO_CLIENTES + fila + fila, encoding="utf-8")
    with pytest.raises(ValueError, match="claves duplicadas"):
        GestorRutasBajio(str(directorio))
