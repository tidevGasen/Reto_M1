# Bitácora de refactorización

**Nombre:** Juan Pablo Alegría
**Matrícula:**
**Fecha:** 2026-10-07
**Herramienta:** Claude Code (app de escritorio, modelo Claude Opus 5.5)

Cada refactorización se hizo con Claude Code, una a la vez, validando con
`pytest` y `ruff check src` antes del commit. Los prompts se copian tal cual.

## 0. Línea base y diagnóstico

Estado inicial (commit `f0b9b6e`, rama `main`):

```text
pytest           -> 20 passed
ruff check src   -> Found 20 errors
  4 UP009  utf8-encoding-declaration      3 SIM102 collapsible-if
  3 SIM115 open-file-with-context-handler 2 C901   complex-structure
  2 N802   invalid-function-name          1 SIM108 if-else-block-instead-of-if-exp
  1 N816   mixed-case-variable-in-global  1 SIM103 needless-bool
  1 UP015  redundant-open-modes           1 I001   unsorted-imports
  1 F401   unused-import
```

**Prompt de diagnóstico:**

> Dados los siguientes documentos de rubrica, especificación y formato de entrega
> adicional al contenido del curso y proyecto a trabajar, ejecuta un diagnostico inicial
> del proyecto

**Code smells detectados (priorizados por la IA):**

| Prioridad | Smell | Dónde |
|---|---|---|
| 1 | Función gigante (validación + cálculo + stock + folio + ticket) e `if` anidados | `gestor.registrar_venta` |
| 2 | Lógica duplicada de descuento/IVA | `gestor.cotizar` |
| 3 | Números mágicos (1000, 500, 0.10, 0.05, 0.02, 200, 0.16, "VIP", 5) | `gestor.py`, `reportes.py` |
| 4 | Nombres crípticos / estilos mezclados (`x`, `aux`, `temp2`, `t`, `hacer_cosa`, `contadorVentas`, `hayArchivo`) | todos |
| 5 | Código muerto (`calcular_descuento_viejo`, `exportar_txt`, `reporteViejoCSV`, `MODO_DEBUG`) | `gestor.py`, `reportes.py` |
| 6 | Archivos sin `with`, `except Exception` genérico | `almacen.py` |
| 7 | Bubble sort manual | `reportes.mas_vendidos` |
| 8 | Sin type hints | todos |
| 9 | Lógica mezclada con E/S (`print` dentro de reportes) | `reportes.py` |
| 10 | Estado global | `gestor.py` (se deja documentado: los tests dependen de él) |

## Configuración de Claude Code

| Versión | Prompt usado | Cambio realizado | Justificación |
|---|---|---|---|
| v1 | `/init` (en la carpeta del proyecto, aislada del material del curso) | `CLAUDE.md` generado: contexto, comandos, reglas, arquitectura | Primer `/init` se corrió en la carpeta del curso y mezclaba PDFs/docx; se movió el proyecto fuera para que el contexto fuera solo el código |

## Mejora CLAUDE.md

| Versión | Prompt usado | Cambio realizado | Justificación |
|---|---|---|---|
| v2 | "Mejora el CLAUDE.md añadiendo detalles especifícos sobre las carácteristicas del proyecto además de listados detallados de lo existente y crea un archivo .claudeignore y corrige .gitignore" | Se agregó: lista exacta de API pública que usan los tests, flujo por refactorización, convenciones de estilo con ejemplos, lista de comportamientos frágiles (mensajes de error, orden de validación, regla VIP, redondeo, formato de ticket). Se creó `.claudeignore`. Se corrigió `.gitignore` (tenía BOM UTF-8 de PowerShell que invalidaba la primera regla) | v1 describía el código pero no decía *cómo* trabajar ni qué detalles se rompen fácilmente; v2 reduce el riesgo de que la IA cambie comportamiento sin que los tests lo detecten |
| v3 | "Dentro de CLAUDE.md necesito que añadas como regla que cada que se te de un prompt sigas el siguiente flujo: 1: Revisión previo a la refactorización, 2: Plan resumido de lo que realizarás en la bitacora indicando la versión del código, 3: Ejecución de cambios, 4: Ejecución de pruebas. En caso de que las pruebas no sean exitosas, repetir 3 y 4 con la salida de las pruebas fallidas (máximo 5 repeticiones; la salida del ciclo es la ejecución exitosa de todas las pruebas). En caso de que sean todas exitosas, ejecutar commit con el cambio realizado con el siguiente formato JSON: [{id, archivo, funcion, cambio}, ...]" | **Plan (versión `12bbc1e`):** reemplazar la sección "Flujo de trabajo por refactorización" (4 pasos) por "Flujo obligatorio para cada prompt". **Cambio:** flujo de 5 pasos con ciclo de corrección acotado a 5 iteraciones, qué hacer si se agotan (revertir, documentar, avisar), versión = hash corto del commit y formato de commit: título Conventional Commits + cuerpo JSON con ejemplo. | Hace el proceso reproducible y auditable: cada cambio deja plan, versión de partida, iteraciones y un commit con detalle estructurado por función. El límite de 5 iteraciones evita ciclos infinitos de "arreglar hasta que pase". Se interpretó "versión" como hash del commit y se agregó un título al commit porque git usa la primera línea como resumen. |

## Red de seguridad: tests de caracterización

**Prompt:**

> Agrega test adicionales de caracterización en un archivo nuevo para no romper los existentes

**Cambio:** se agregó `tests/test_caracterizacion.py` (archivo nuevo; los tests
originales no se tocaron) con 29 casos que fijan lo que la suite original no
cubría: texto exacto del ticket con y sin descuento, campos de la venta,
umbrales de descuento en 500/1000 (incluyendo los valores frontera), regla VIP
(`> 200` estricto, prefijo sensible a mayúsculas), que `cotizar` no aplica VIP,
todos los mensajes de `ultimo_error` y su orden de validación, formato exacto
de `reporte_inventario` y `resumen_ventas` (texto devuelto **e** impreso),
umbral de stock bajo, empates en `mas_vendidos`, archivo JSON corrupto,
estructura del JSON guardado y que `reiniciar_sistema` conserve los mismos
objetos (`almacen` depende de ello).

**Justificación:** la suite original solo revisa totales y algunos casos;
una refactorización podría cambiar el ticket o un mensaje de error y seguir
"en verde". Se escribieron **antes** de tocar el código y se verificó que
pasan con el código original, así describen el comportamiento real.

**Resultado:** `pytest` → 49 passed (20 originales + 29 nuevos). Ruff sin cambios (20).

## Refactorizaciones

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK | Ruff |
|----|--------------|------------------|---------------|----------|------|
| 1  | "Realiza una limpieza de código, optimizando el código existente, no cambiando su funcionalidad" | **Plan (versión `31e9268`):** eliminar código muerto y obsoleto + arreglos triviales de ruff. **Cambio:** se eliminaron `calcular_descuento_viejo`, el bloque comentado `exportar_txt` y la constante sin uso `MODO_DEBUG` (`gestor.py`), `reporteViejoCSV` e `import os` sin uso (`reportes.py`); se reemplazó el docstring obsoleto de `gestor.py` ("lo fueron parchando varias personas..."); `ruff --fix` quitó los 4 encabezados `# -*- coding: utf-8 -*-`, el modo `"r"` redundante en `almacen.cargar_datos` y ordenó los imports de `main.py`. Antes de borrar se verificó con grep que nada en `src/` ni `tests/` usaba ese código. | El código muerto confunde ("¿se usa?, ¿lo puedo borrar?") y agrega superficie de mantenimiento; git conserva el historial si algún día se necesita. Los encabezados `coding` son innecesarios en Python 3. | ✅ 49 passed (1 iteración) | 20 → 11 |
| 2  | "Realiza una optimización al código existente sin modificar la funcionalidad" | **Plan (versión `e3e59d0`):** reemplazar el bubble sort por `sorted`, bucles de filtrado/suma por comprensiones y `sum`, concatenación de strings en bucles por `join`, y copias elemento a elemento por `update`/`extend`. **Cambio:** `reportes.mas_vendidos`: bubble sort O(n²) → acumulación con `dict.get` + `sorted(..., reverse=True)` O(n log n); `total_vendido`: bucle → `sum`; `productos_stock_bajo` y `gestor.buscarProducto`: bucles con `append` → comprensiones (y `texto.lower()` se calcula una vez, no por producto); `reporte_inventario` y `resumen_ventas`: concatenación repetida de strings → lista de líneas + `"\n".join` con f-strings; `almacen.cargar_datos`: copia elemento a elemento → `update`/`extend` (conservando `.clear()` para no romper las referencias compartidas). 51 líneas eliminadas, 30 agregadas. | Algoritmo más eficiente y código idiomático más corto. Riesgo revisado: en empates el bubble sort con `<` estricto conservaba el orden original; `sorted` es estable también con `reverse=True`, así que el resultado es idéntico (lo cubre `test_mas_vendidos_por_defecto_regresa_3_y_respeta_empates`). Las sumas recorren en el mismo orden, por lo que el redondeo de flotantes no cambia. | ✅ 49 passed (1 iteración) | 11 → 11 |
| 3  | "Divide registrar_venta en funciones pequeñas: valida con guard clauses respetando el orden de mensajes de error, extrae el cálculo de descuento (volumen + VIP) e IVA en una función que también use cotizar, y extrae el armado del ticket. Reemplaza los números mágicos por constantes con nombre. Debe eliminar los C901, SIM102 y SIM108 de ruff." | **Plan (versión `5e26e7c`):** constantes de negocio; `_validar_venta` (guard clauses, mismo orden de mensajes); `_descuento_por_volumen`, `_es_vip` y `calcular_importes` compartida con `cotizar`; `_armar_ticket`; `registrar_venta` solo orquesta. **Cambio:** `gestor.py`: constantes `TASA_IVA`, `UMBRAL_DESCUENTO_ALTO/MEDIO`, `TASA_DESCUENTO_ALTO/MEDIO`, `PREFIJO_VIP`, `MONTO_MINIMO_VIP`, `TASA_EXTRA_VIP`; 4 `if` anidados → `_validar_venta` con guard clauses que regresa el mensaje; `_descuento_por_volumen` + `_es_vip` + `calcular_importes(subtotal, cliente)` que devuelve `(descuento, impuesto, total)` y ahora usa también `cotizar` (sin cliente → sin VIP, igual que antes); `_armar_ticket` con lista de líneas; `registrar_venta` pasó de 76 a 30 líneas y solo orquesta. `reportes.py`: `STOCK_MINIMO = 5`. | Cada función tiene una responsabilidad y se puede probar sola; la regla de descuento vive en un solo lugar (antes duplicada en `cotizar`, con riesgo de que divergieran); las constantes documentan el negocio. Detalles conservados a propósito: descuento `0` entero (no `0.0`) cuando no aplica, porque se guarda así en el JSON; la línea "Descuento" del ticket se decide con el descuento **sin redondear**; orden de mensajes de error. Además de pytest se comparó la salida completa de 5 ventas + 1 cotización contra la versión `5e26e7c`: idéntica. El C901 de `main.menu` queda para otra refactorización (fuera del alcance de `registrar_venta`). | ✅ 49 passed (1 iteración) | 11 → 6 |
| 4  | "Usa with open en almacen.py y simplifica hayArchivo, añade excepciones específicas" | **Plan (versión `7e7f579`):** `with open` en `guardar_datos` y `cargar_datos`; `except Exception` → `except (json.JSONDecodeError, UnicodeDecodeError)`; `hayArchivo` regresa directamente `os.path.exists`. **Cambio:** `guardar_datos` y `cargar_datos` usan `with open(...)` (el archivo se cierra aunque ocurra un error, sin `f.close()` manuales repetidos en cada rama); `except Exception` → `except (json.JSONDecodeError, UnicodeDecodeError)`, que son exactamente los dos fallos de un archivo corrupto (JSON inválido o bytes que no son UTF-8); el diccionario de `guardar_datos` se construye con literal; `hayArchivo` pasa de `if/else` que regresa `True`/`False` a `return os.path.exists(ruta)` y su comentario a docstring. Se mantuvo el nombre `hayArchivo` (renombrar es otra refactorización). | `except Exception` ocultaba errores de programación (p. ej. un `NameError` también se reportaría como "archivo corrupto"); ahora solo se atrapa lo esperado. `with` garantiza el cierre del archivo. Se verificó además, contra la versión `7e7f579`, que un archivo en Latin-1 sigue reportando "archivo corrupto" y que el archivo queda liberado (se pudo borrar) en ambos casos. | ✅ 49 passed (1 iteración) | 6 → 3 |
| 5  |              |                  |               |          |      |

## Intentos fallidos y correcciones

| Qué pasó | Cómo se detectó | Cómo se resolvió |
|---|---|---|
| `.gitignore` creado con `Out-File` quedó con BOM y la regla `__pycache__/` no aplicaba | Revisión de los bytes del archivo (`od -c`) | Se reescribió sin BOM |
| Refactorización 1: el reemplazo por script de `calcular_descuento_viejo`/`exportar_txt` no encontró el texto (diferencias de escape/saltos de línea) y el bloque quedó en el archivo | El grep de verificación posterior seguía mostrando `calcular_descuento_viejo` | Se eliminó con edición directa del bloque exacto; lección: verificar siempre después de un cambio automatizado, no asumir que se aplicó |
| Refactorización 3: al comparar la salida antes/después con `hash(tuple(...))` los valores salieron distintos | Los hashes no coincidían aunque pytest pasaba | Falsa alarma: Python aleatoriza `hash()` de strings por proceso (`PYTHONHASHSEED`). Se repitió comparando el texto completo con `diff`: idéntico. Lección: elegir bien la herramienta de verificación |
| Refactorización 3 (detectado en la 4): la comparación con `diff` de la R3 **no era válida**: el código viejo se extrajo en `/tmp`, ruta que el Python de Windows no ve, así que ambas corridas importaron el código nuevo de `src/` | Al repetir la técnica en la R4, Python no encontró `/tmp`; se sospechó que en la R3 había pasado lo mismo sin error visible | Se repitió la comparación de la R3 con rutas de Windows e imprimiendo qué archivo `gestor.py` se cargó en cada corrida (`5e26e7c` vs `7e7f579`): 7 líneas idénticas. La conclusión de la R3 se mantiene, ahora con evidencia válida. Lección: una verificación que no puede fallar no verifica nada; comprobar que realmente se ejecuta la versión que se cree |

## Variaciones de prompts

| Refactorización | Prompt | Qué hizo la IA | Observación |
|---|---|---|---|
| 1 | Vago: "Realiza una limpieza de código, optimizando el código existente, no cambiando su funcionalidad" | Por la regla de `CLAUDE.md` ("un solo tipo de refactorización por prompt") lo acotó a **limpieza** (código muerto + arreglos triviales de ruff) y dejó "optimizar" (bubble sort, sumas manuales) para otra refactorización | Un prompt vago podía mezclar varios cambios en un commit; el `CLAUDE.md` funcionó como guardarraíl. Un prompt explícito ("elimina X, Y, Z; verifica con grep") habría evitado que la IA tuviera que interpretar |
| 2 | Vago: "Realiza una optimización al código existente sin modificar la funcionalidad" | Lo limitó a optimización algorítmica/idiomática (bubble sort, bucles, concatenaciones) sin renombrar ni dividir funciones; identificó por su cuenta el riesgo de estabilidad del ordenamiento en empates | Al tener los tests de caracterización, la IA pudo apoyarse en un test concreto para justificar que `sorted` no cambia el resultado. Un prompt vago funciona mejor cuando el `CLAUDE.md` y los tests acotan el espacio de cambios |
| 3 | Explícito: qué dividir, qué conservar (orden de errores), qué reutilizar (`cotizar`) y criterio de éxito medible (reglas de ruff a eliminar) | Ejecutó exactamente lo pedido sin interpretar; señaló que "los C901" incluía también `main.menu`, que no era parte de la función, y lo dejó fuera | El prompt explícito con criterio de aceptación verificable (ruff) dejó claro cuándo terminar. Aun así la IA tuvo que detectar una ambigüedad ("los C901") — conviene nombrar exactamente qué errores |
