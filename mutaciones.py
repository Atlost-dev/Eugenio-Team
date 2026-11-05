"""Técnica de mutación: inyecta un error a la vez en una copia del código y corre la suite.

Una mutación está "detectada" si al menos una prueba falla con el error inyectado.
El código original nunca se modifica: cada mutación trabaja en una carpeta temporal.
Ejecutar: .venv/bin/python mutaciones.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# (id, archivo, texto original, texto mutado, descripción)
MUTACIONES = [
    ("M-01", "gestor.py", 'if self.buscar_cliente(cliente.id_cliente):\n            raise ValueError(f"Ya existe el cliente',
     'if False:\n            raise ValueError(f"Ya existe el cliente',
     "crear_cliente acepta ids duplicados"),
    ("M-02", "gestor.py", '"en_transito": ("entregado",)', '"en_transito": ("entregado", "cancelado")',
     "se permite en_transito -> cancelado"),
    ("M-03", "gestor.py", 'if pedido.estado != "pendiente":\n            raise ValueError("Un pedido nuevo',
     'if False:\n            raise ValueError("Un pedido nuevo',
     "crear_pedido acepta un estado inicial distinto de pendiente"),
    ("M-04", "gestor.py", 'ultimo = max(ultimo, int(filas[0]["ultimo_folio"]))', 'pass',
     "cargar ignora secuencias.csv (el folio se reutiliza)"),
    ("M-05", "modelos.py", "10 <= len(re.sub(r\"\\D\", \"\", self.telefono)) <= 15",
     "10 <= len(re.sub(r\"\\D\", \"\", self.telefono)) < 15",
     "límite del teléfono desplazado (15 dígitos se rechaza)"),
    ("M-06", "modelos.py", "if numero <= 0:", "if numero < 0:", "entero_positivo acepta 0"),
    ("M-07", "gestor.py", 'if (pedido.origen, pedido.destino) != (ruta.origen, ruta.destino):\n                raise ValueError("La ruta no coincide',
     'if False:\n                raise ValueError("La ruta no coincide',
     "_validar_relaciones no compara el trayecto"),
    ("M-08", "gestor.py", "if disponible and not ruta.disponible:", "if False:",
     "_validar_relaciones ignora la disponibilidad"),
    ("M-09", "gestor.py", 'if any(p.id_cliente == cliente.id_cliente for p in self.pedidos):',
     'if False:', "eliminar_cliente borra clientes con pedidos"),
    ("M-10", "gestor.py", 'if not any(c.id_cliente == pedido.id_cliente for c in clientes):',
     'if False:', "cargar acepta pedidos con cliente inexistente"),
    ("M-11", "gestor.py", 'if len(claves) != len(set(claves)):', 'if False:',
     "cargar acepta claves duplicadas dentro de un CSV"),
    ("M-12", "gestor.py", 'if (pedido.origen, pedido.destino) != (nueva.origen, nueva.destino):',
     'if False:', "actualizar_ruta cambia el trayecto de una ruta con pedidos"),
    ("M-13", "modelos.py", 'if estado in ("en_transito", "entregado") and self.id_ruta is None:',
     'if False:', "Pedido en tránsito o entregado sin ruta"),
    ("M-14", "gestor.py", 'if lector.fieldnames != campos:', 'if False:',
     "_leer acepta encabezados incorrectos"),
]


def correr(mutacion):
    ident, archivo, original, mutado, _ = mutacion
    with tempfile.TemporaryDirectory(prefix="mutacion_") as carpeta:
        copia = Path(carpeta)
        shutil.copytree(RAIZ / "rutas_bajio", copia / "rutas_bajio")
        shutil.copytree(RAIZ / "tests", copia / "tests")
        shutil.copy(RAIZ / "pytest.ini", copia / "pytest.ini")
        fuente = copia / "rutas_bajio" / archivo
        codigo = fuente.read_text(encoding="utf-8")
        # Una mutación que no encuentra su texto invalidaría el experimento: se aborta.
        assert codigo.count(original) == 1, f"{ident}: el texto original no aparece exactamente una vez"
        fuente.write_text(codigo.replace(original, mutado), encoding="utf-8")
        salida = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                                cwd=copia, capture_output=True, text=True)
        fallidas = [linea.split(" - ")[0].removeprefix("FAILED ")
                    for linea in salida.stdout.splitlines() if linea.startswith("FAILED")]
        return salida.returncode != 0, fallidas


if __name__ == "__main__":
    detectadas = 0
    for mutacion in MUTACIONES:
        detectada, fallidas = correr(mutacion)
        detectadas += detectada
        print(f"{mutacion[0]} | {'DETECTADA' if detectada else 'SOBREVIVE'} | {mutacion[4]}")
        for prueba in fallidas:
            print(f"      falla: {prueba}")
    print(f"\nDetectadas: {detectadas} de {len(MUTACIONES)}")
