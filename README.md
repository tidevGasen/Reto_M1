# Reto: Refactorización Asistida por IA

## Gestor de inventario y ventas — Tienda "La Esquina"

Aplicación de consola en Python para administrar el inventario y las ventas de
una tienda pequeña: alta de productos, registro de ventas con descuentos e IVA,
cotizaciones, alertas de stock bajo, reporte de más vendidos y persistencia de
datos en JSON.

El código original funcionaba, pero estaba lleno de *code smells* (función
gigante, lógica duplicada, números mágicos, nombres crípticos, código muerto,
archivos sin `with`...). En la rama `refactorizacion` se mejoró **sin cambiar
su comportamiento**, usando Claude Code como asistente. El proceso completo
está en [`docs/bitacora.md`](docs/bitacora.md).

| | Código original (`main`) | Refactorizado (`refactorizacion`) |
|---|---|---|
| `ruff check src` | 20 errores | **0 errores** |
| `pytest` | 20 passed | **49 passed** (20 originales + 29 de caracterización) |
| Complejidad ciclomática máxima | 17 (`menu`), 12 (`registrar_venta`) | ≤ 10 en todas las funciones |
| Type hints | ninguno | todas las funciones + `TypedDict` |
| Refactorizaciones | — | 8, una por commit |

## Estructura del proyecto

```
.
├── CLAUDE.md                # Instrucciones y reglas para Claude Code
├── .claudeignore            # Archivos que Claude Code no debe leer
├── src/
│   ├── gestor.py            # Lógica de productos y ventas (estado global)
│   ├── almacen.py           # Carga y guardado de datos (JSON, escritura atómica)
│   ├── reportes.py          # Reportes e indicadores
│   └── main.py              # Menú interactivo de consola
├── tests/
│   ├── test_gestor.py       # Suite original (sin modificar)
│   ├── test_almacen.py      # Suite original (sin modificar)
│   ├── test_reportes.py     # Suite original (sin modificar)
│   └── test_caracterizacion.py  # Agregado: fija el comportamiento antes de refactorizar
├── docs/
│   ├── bitacora.md          # Registro de cada refactorización (prompt, cambio, justificación, tests)
│   ├── reflexion.md         # Aprendizajes y conclusiones
│   └── evidencia/           # Logs de pytest, ruff e integridad
├── datos_ejemplo.json       # Datos de ejemplo para el menú interactivo
├── requirements.txt
└── pyproject.toml           # Configuración del linter (ruff) — sin modificar
```

## Requisitos previos

- Python **3.10 o superior** (probado con Python 3.14.8 en Windows 11)
- Git
- Dependencias (en `requirements.txt`): `pytest` y `ruff`

## Instalación

```bash
# 1. Clonar el repositorio y cambiar a la rama refactorizada
git clone https://github.com/tidevGasen/Reto_M1.git
cd Reto_M1
git checkout refactorizacion

# 2. Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
# Tests (deben pasar TODOS)
pytest

# Una sola prueba
pytest tests/test_gestor.py::test_venta_cliente_vip_recibe_descuento_extra

# Linter (debe terminar con 0 errores)
ruff check src

# Aplicación interactiva (lee y escribe datos_ejemplo.json en el directorio actual)
cd src && python main.py
```

## Evidencia de tests pasando

Logs completos en [`docs/evidencia/`](docs/evidencia/), generados sobre el
commit `4ddb755` con Python 3.14.8.

### pytest — 49 passed ([log completo](docs/evidencia/pytest.log))

```text
$ pytest -v
tests/test_almacen.py ...                       3 passed
tests/test_caracterizacion.py ...              29 passed
tests/test_gestor.py ...                       13 passed
tests/test_reportes.py ...                      4 passed
============================= 49 passed in 0.17s ==============================
```

### ruff — 0 errores ([log completo](docs/evidencia/ruff.log))

```text
$ ruff check src
All checks passed!
```

### Antes de refactorizar ([log completo](docs/evidencia/antes.log))

```text
$ ruff check src --statistics          # commit f0b9b6e, código original
4  UP009   utf8-encoding-declaration        3  SIM102  collapsible-if
3  SIM115  open-file-with-context-handler   2  C901    complex-structure
2  N802    invalid-function-name            1  SIM108  if-else-block-instead-of-if-exp
1  N816    mixed-case-variable-in-global    1  SIM103  needless-bool
1  UP015   redundant-open-modes             1  I001    unsorted-imports
1  F401    unused-import
Found 20 errors.

$ pytest -q
20 passed
```

### Integridad: tests originales y configuración sin modificar ([log completo](docs/evidencia/integridad.log))

```text
$ git diff --stat f0b9b6e HEAD -- tests/conftest.py tests/test_almacen.py \
      tests/test_gestor.py tests/test_reportes.py pyproject.toml
(sin salida = sin cambios)

$ git diff --stat f0b9b6e HEAD -- tests/
 tests/test_caracterizacion.py | 230 +++++   (único archivo de tests: nuevo)
```

### Validación incremental

Cada refactorización se validó con `pytest` y `ruff check src` **antes** de su
commit. Las pruebas pasaron en la primera iteración en los 8 casos:

| Commit | Refactorización | Tests | Ruff |
|---|---|---|---|
| `12bbc1e` | Tests de caracterización (red de seguridad) | 49 ✅ | 20 |
| `e3e59d0` | 1. Elimina código muerto y arreglos triviales | 49 ✅ | 20 → 11 |
| `5e26e7c` | 2. Optimiza bucles; bubble sort → `sorted` | 49 ✅ | 11 |
| `7e7f579` | 3. Divide `registrar_venta`; constantes de negocio | 49 ✅ | 11 → 6 |
| `eb0ff4e` | 4. `with open` y excepciones específicas | 49 ✅ | 6 → 3 |
| `3f78f04` | 5. Renombra a snake_case descriptivo | 49 ✅ | 3 → 1 |
| `16aee04` | 6. Menú con diccionario de opciones | 49 ✅ | 1 → 0 |
| `b0befa2` | 7. Guardado con escritura atómica | 49 ✅ | 0 |
| `4ddb755` | 8. Type hints y `TypedDict` | 49 ✅ | 0 |

Además de pytest, en las refactorizaciones que tocan código sin cobertura de
tests (`main.py`, formato del JSON) se comparó la salida real del programa
contra la versión anterior; los detalles están en la bitácora.

## Reglas del reto

- No se modificaron los archivos originales de `tests/` ni `pyproject.toml`
  (solo se **agregó** `tests/test_caracterizacion.py`).
- El código de `src/` pasa `ruff check src` sin errores.
- `agregarProducto` y `buscarProducto` conservan su nombre porque los tests los usan.
- El comportamiento observable del programa se mantiene idéntico.

## Criterios de evaluación

| Criterio | Descripción | Peso |
|----------|-------------|------|
| Configuración | `CLAUDE.md` y `.claudeignore` completos y pertinentes | 15% |
| Calidad de refactorizaciones | ≥5 refactorizaciones significativas, bien elegidas y bien ejecutadas | 30% |
| Tests pasando | La suite completa pasa al final (y después de cada cambio) | 20% |
| Bitácora | Prompts documentados, cambios explicados y justificados | 25% |
| Reflexión | Análisis crítico del trabajo con la IA | 10% |
