# CLAUDE.md

Guía para Claude Code en este repositorio. Responder siempre en español.

## Contexto

Reto de refactorización: app de consola en Python (Python ≥ 3.10) que gestiona inventario y ventas de la tienda "La Esquina" (productos, ventas con descuentos e IVA, cotizaciones, stock bajo, más vendidos, persistencia JSON). El código funciona pero está lleno de code smells a propósito; el objetivo es refactorizarlo **sin cambiar el comportamiento observable**. El código y los mensajes están en español.

## Comandos

Usar el venv del proyecto (`.venv`; en Windows `.venv\Scripts\activate`).

```bash
pip install -r requirements.txt
pytest                              # suite completa (debe pasar TODA, tras cada refactorización)
pytest tests/test_gestor.py::nombre_test   # una sola prueba
ruff check src                      # debe terminar con 0 errores al final del reto
ruff check src --fix                # solo arregla lo trivial
cd src && python main.py            # menú interactivo (lee/escribe ../datos_ejemplo.json relativo al cwd: ARCHIVO = "datos_ejemplo.json")
```

## Reglas del reto (no negociables)

- **No modificar `tests/` ni `pyproject.toml`.** Si un test falla, la refactorización cambió el comportamiento: corregir el código, no la prueba.
- Los nombres `agregarProducto` y `buscarProducto` se conservan (los tests los usan; están en `ignore-names` de ruff). Cualquier otro nombre puede renombrarse a snake_case, pero antes hay que buscarlo en `tests/` con grep. API que los tests usan y **no** se puede renombrar: `gestor.INVENTARIO`, `gestor.VENTAS`, `gestor.reiniciar_sistema`, `agregarProducto`, `buscarProducto`, `eliminar_producto`, `actualizar_stock`, `registrar_venta`, `cotizar`, `almacen.guardar_datos`, `almacen.cargar_datos`, `reportes.productos_stock_bajo`, `reportes.total_vendido`, `reportes.mas_vendidos`, `reportes.reporte_inventario`.
- Ruff (`pyproject.toml`) selecciona E, W, F, I, N, B, SIM, UP y C90 con `max-complexity = 10`, línea de 88 columnas. Los tests no se lintean.
- Validar con `pytest` **y** `ruff check src` después de cada refactorización; commits atómicos (uno por refactorización) en la rama `refactorizacion`, entrega por PR hacia `main`. Documentar cada prompt/cambio en `docs/bitacora.md` y la reflexión en `docs/reflexion.md`.
- Se permite **agregar** archivos de prueba nuevos (p. ej. `tests/test_caracterizacion.py`) para fijar comportamiento antes de refactorizar, pero nunca editar los existentes.

## Flujo de trabajo por refactorización

1. Explicar primero qué se va a cambiar y por qué (sin tocar código).
2. Aplicar **un solo tipo** de refactorización por paso; no mezclar renombrados con cambios de lógica.
3. Correr `pytest` y `ruff check src`; reportar el conteo de tests y de errores de ruff antes/después.
4. Mostrar el diff y proponer el mensaje de commit (Conventional Commits en español: `refactor: ...`, `docs: ...`, `test: ...`).

## Convenciones de estilo

- Funciones, variables y módulos en `snake_case`; constantes en `MAYUSCULAS`; nombres descriptivos en español (`subtotal`, `descuento`, `producto`, no `aux`, `temp2`, `x`, `t`).
- Type hints en todas las funciones (`def cotizar(codigo: str, cantidad: int) -> float | None:`); usar sintaxis 3.10 (`X | None`, `list[dict]`).
- Docstrings en español, una línea cuando baste. Sin comentarios que repitan el código.
- Números de negocio como constantes con nombre al inicio del módulo, p. ej.:

  ```python
  TASA_IVA = 0.16
  UMBRAL_DESCUENTO_ALTO = 1000
  STOCK_MINIMO = 5
  ```

- Validaciones con *guard clauses* (retorno temprano) en lugar de `if` anidados.
- Archivos siempre con `with open(...)`.
- Separar cálculo de presentación: las funciones de negocio no hacen `print`.

## Comportamiento que NO debe cambiar (fácil de romper)

- Mensajes exactos de `ultimo_error`: `"codigo vacio"`, `"el producto ya existe"`, `"precio invalido"`, `"stock invalido"`, `"producto no existe"`, `"el stock no puede quedar negativo"`, `"stock insuficiente"`, `"cantidad invalida"`, `"el archivo no existe"`, `"archivo corrupto"`.
- Orden de validación en `registrar_venta`: código vacío → producto no existe → cantidad inválida → stock insuficiente. En `cotizar` el orden es distinto (producto no existe → cantidad inválida) y **no** aplica el extra VIP.
- El extra VIP es 2 % **del subtotal** (no de la base) y solo si `subtotal - descuento > 200` (estrictamente mayor).
- Redondeo: `round(..., 2)` por campo; `total = round(base + impuesto, 2)` usando el impuesto sin redondear.
- Ticket: la línea `Descuento: -$...` solo aparece si el descuento > 0; los números se formatean con `str()` (p. ej. `$23.2`, no `$23.20`).
- `reporte_inventario` y `resumen_ventas` imprimen **y** regresan el texto.

## Arquitectura

Todo el estado vive como **globales de módulo en `src/gestor.py`**: `INVENTARIO` (dict código → dict producto), `VENTAS` (lista de dicts), `contadorVentas` (folio) y `ultimo_error` (último mensaje de error). Los demás módulos dependen de `gestor` y mutan/leen ese estado directamente:

- `gestor.py` — lógica de negocio. Las funciones reportan fallos devolviendo `False`/`None` y dejando el motivo en `ultimo_error` (no lanzan excepciones). `registrar_venta` calcula descuento por volumen (≥500 → 5 %, ≥1000 → 10 %), extra VIP de 2 % (cliente que empieza con "VIP" y subtotal−descuento > 200), IVA 16 %, descuenta stock, genera folio y arma el ticket en texto. `cotizar` duplica el cálculo de descuento/IVA (sin el extra VIP) sin registrar nada.
- `almacen.py` — persistencia JSON: `guardar_datos`/`cargar_datos` escriben y reemplazan el estado global de `gestor` (incluida la asignación a `gestor.contadorVentas` y `gestor.ultimo_error`, por lo que esas globales deben seguir accesibles como atributos del módulo).
- `reportes.py` — reportes que **imprimen y además devuelven** el texto (`reporte_inventario`, `resumen_ventas`); umbral de stock bajo = 5 en `productos_stock_bajo` y en `reporte_inventario`. `mas_vendidos` devuelve lista de `(codigo, unidades)`.
- `main.py` — menú interactivo; mezcla I/O con llamadas a `gestor`/`reportes`/`almacen` y lee `gestor.ultimo_error` para mostrar errores.

Los tests (`tests/conftest.py`) insertan `src/` en `sys.path`, importan `gestor` como módulo plano (sin paquete) y llaman `gestor.reiniciar_sistema()` antes y después de cada prueba; los módulos se importan entre sí por nombre simple (`import gestor`), así que no convertir `src` en paquete sin ajustar eso.

Código muerto conocido (candidato a eliminar): `calcular_descuento_viejo`, bloque comentado `exportar_txt` en `gestor.py` y `reporteViejoCSV` en `reportes.py`.
