import pytest

from rutas_bajio.gestor import GestorRutasBajio
from rutas_bajio.modelos import Cliente, Pedido, Ruta


@pytest.fixture
def directorio(tmp_path):
    """Carpeta temporal para los CSV; nunca se usa datos_notebook/."""
    return tmp_path / "datos"


@pytest.fixture
def gestor(directorio):
    """Gestor vacío sobre archivos temporales."""
    return GestorRutasBajio(str(directorio))


@pytest.fixture
def cliente():
    return Cliente("CLI-010", "Constructora Guanajuato S.A.", "Guanajuato Capital", "473-100-2233")


@pytest.fixture
def ruta():
    return Ruta("RUTA-03", "León", "Guanajuato Capital", 55, 1.5, "Julián Pérez")


@pytest.fixture
def gestor_con_datos(gestor, cliente, ruta):
    """2 clientes, 3 rutas (una no disponible) y un pedido pendiente."""
    gestor.crear_cliente(cliente)
    gestor.crear_cliente(Cliente("CLI-011", "Ferretera Industrial", "León", "477-200-3344"))
    gestor.crear_ruta(ruta)
    gestor.crear_ruta(Ruta("RUTA-01", "León", "Irapuato", 30, 0.6, "Miguel Ángel Torres"))
    gestor.crear_ruta(Ruta("RUTA-02", "León", "Celaya", 95, 2.0, "Rosa Elena Vázquez", disponible=False))
    gestor.crear_pedido(Pedido("PED-0001", "CLI-010", "Láminas de acero", 40,
                               "León", "Guanajuato Capital", "2026-09-15", id_ruta="RUTA-03"))
    return gestor
