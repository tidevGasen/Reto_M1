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
| 2  |              |                  |               |          |      |
| 3  |              |                  |               |          |      |
| 4  |              |                  |               |          |      |
| 5  |              |                  |               |          |      |

## Intentos fallidos y correcciones

| Qué pasó | Cómo se detectó | Cómo se resolvió |
|---|---|---|
| `.gitignore` creado con `Out-File` quedó con BOM y la regla `__pycache__/` no aplicaba | Revisión de los bytes del archivo (`od -c`) | Se reescribió sin BOM |
| Refactorización 1: el reemplazo por script de `calcular_descuento_viejo`/`exportar_txt` no encontró el texto (diferencias de escape/saltos de línea) y el bloque quedó en el archivo | El grep de verificación posterior seguía mostrando `calcular_descuento_viejo` | Se eliminó con edición directa del bloque exacto; lección: verificar siempre después de un cambio automatizado, no asumir que se aplicó |

## Variaciones de prompts

| Refactorización | Prompt | Qué hizo la IA | Observación |
|---|---|---|---|
| 1 | Vago: "Realiza una limpieza de código, optimizando el código existente, no cambiando su funcionalidad" | Por la regla de `CLAUDE.md` ("un solo tipo de refactorización por prompt") lo acotó a **limpieza** (código muerto + arreglos triviales de ruff) y dejó "optimizar" (bubble sort, sumas manuales) para otra refactorización | Un prompt vago podía mezclar varios cambios en un commit; el `CLAUDE.md` funcionó como guardarraíl. Un prompt explícito ("elimina X, Y, Z; verifica con grep") habría evitado que la IA tuviera que interpretar |
