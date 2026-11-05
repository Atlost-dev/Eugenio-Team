# Rutas del Bajío — Eugenio Team

Backend del caso de estudio **Rutas del Bajío** (Análisis de Procesos de la Industria, Parcial 2). Gestiona clientes, rutas y pedidos de una empresa de logística con:

- **CRUD** de las tres entidades, con validación de datos (claves `CLI-NNN`, `RUTA-NN`, `PED-NNNN`, ciudades del catálogo, fechas `AAAA-MM-DD`).
- **Composición por llaves foráneas**: un pedido solo existe si su cliente existe, y su ruta debe hacer el mismo trayecto y estar disponible.
- **Persistencia en CSV** (`clientes.csv`, `rutas.csv`, `pedidos.csv`, `secuencias.csv`) con escritura atómica.
- **Máquina de estados del pedido**: `pendiente → en_transito → entregado` y `pendiente → cancelado`; cualquier otra transición se rechaza.
- **Suite de pruebas con pytest** (71 pruebas) y un script de **mutaciones** que comprueba que la suite detecta errores.

No incluye interfaz gráfica: el curso se concentra en la lógica de negocio.

## Equipo

| Integrante | Rol |
|---|---|
| Edgar Daniel Zuñiga Gonzalez | Arquitecto |
| Cristian Ibrahim Salomon Marquez | Desarrollador CRUD |
| Edgar Alexis Sánchez Huerta | Encargado de Pruebas |
| Luis Mario Juarez Rolón | Documentador |

Profesor: Eugenio Salvador Martínez Velázquez.

## Estructura

```
Eugenio-Team/
├── Desarrollo.ipynb        Cuaderno original del equipo (desarrollo en clase)
├── rutas_bajio/            Código del sistema, copiado sin cambios del cuaderno
│   ├── modelos.py          Validadores y entidades: Cliente, Ruta, Pedido
│   └── gestor.py           GestorRutasBajio: CRUD, relaciones, estados y CSV
├── tests/                  Suite de pytest (conftest.py + un archivo por área)
├── mutaciones.py           Técnica de mutación sobre una copia temporal del código
├── main.py                 Punto de entrada (ver "Problemas conocidos")
├── pytest.ini              Configuración de pytest y marcadores
├── requirements.txt        Dependencias
└── docs/                   Actas, Capítulo 3 (pruebas) y evidencias de ejecución
```

## Descarga e instalación

Requisitos: **Python 3.10 o superior** y **Git**.

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/faimercub32/Eugenio-Team.git
   cd Eugenio-Team
   ```

   Sin Git: en GitHub, botón **Code → Download ZIP**, descomprimir y abrir una terminal en la carpeta.

2. Crear un entorno virtual del proyecto (las dependencias se instalan solo ahí, no en todo el equipo):

   ```bash
   python3 -m venv .venv
   ```

   En Windows: `py -m venv .venv`

3. Activar el entorno e instalar las dependencias:

   | Sistema | Activar |
   |---|---|
   | macOS / Linux | `source .venv/bin/activate` |
   | Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
   | Windows (cmd) | `.venv\Scripts\activate.bat` |

   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Todos los comandos se corren desde la carpeta del proyecto con el entorno activado.

### Pruebas

```bash
pytest                        # suite completa (71 pruebas)
pytest -v                     # con el nombre de cada prueba
pytest -m csv                 # solo lectura y escritura de CSV
pytest -m integracion         # solo pruebas de integración
pytest -m "not integracion"   # todo menos integración (uso diario)
```

Las pruebas trabajan siempre en carpetas temporales: nunca modifican datos reales.

### Mutaciones

```bash
python mutaciones.py
```

Inyecta 14 errores, uno a la vez, en una copia temporal de `rutas_bajio/` y corre la suite. Cada línea indica si la mutación fue **DETECTADA** (alguna prueba falló, que es lo esperado) o **SOBREVIVE** (ninguna prueba la protege). El código del repositorio no se modifica.

### Usar el sistema desde Python

```python
from rutas_bajio.gestor import GestorRutasBajio
from rutas_bajio.modelos import Cliente, Ruta

gestor = GestorRutasBajio("datos")   # carpeta donde se guardan los CSV
gestor.crear_cliente(Cliente("CLI-010", "Constructora Guanajuato", "Guanajuato Capital", "4731002233"))
gestor.crear_ruta(Ruta("RUTA-03", "León", "Guanajuato Capital", 55, 1.5, "Julián Pérez"))

pedido = gestor.registrar_pedido("CLI-010", "Láminas de acero", 40, "León",
                                 "Guanajuato Capital", "2026-09-15", id_ruta="RUTA-03")
gestor.cambiar_estado(pedido.folio, "en_transito")
print(gestor.detalle_pedido(pedido.folio))
```

Los datos quedan en `datos/` y se vuelven a cargar al crear otro `GestorRutasBajio("datos")`.

### Cuaderno

`Desarrollo.ipynb` se abre en Google Colab, VS Code o Jupyter (`pip install notebook` y luego `jupyter notebook`). Guarda sus datos en `datos_notebook/`, que está excluida del repositorio.

## Documentación

- [`docs/Acta_Encargado_de_Pruebas.md`](docs/Acta_Encargado_de_Pruebas.md) y [`docs/Acta_Documentador.md`](docs/Acta_Documentador.md): actas de clase.
- [`docs/Capitulo3_Pruebas.pdf`](docs/Capitulo3_Pruebas.pdf): estrategia y resultados de pruebas (matriz unificada de 47 criterios, mutaciones, defectos y límites).
- [`docs/evidencias/`](docs/evidencias/): salidas reales de pytest y de las mutaciones.

## Problemas conocidos

- **`main.py` no se ejecuta** (`ImportError`): importa `rutas_bajio.consola`, que no existe, y usa una firma de `crear_pedido` distinta de la del paquete. Registrado como defecto D-3 en el Capítulo 3. Mientras tanto, usar el sistema desde Python o desde el cuaderno.
- **Carga por lote** (`rutas_bajio/lotes.py`): diseñada en el Acta del Documentador, no implementada.
