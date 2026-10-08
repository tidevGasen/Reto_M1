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

## Refactorizaciones

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK | Ruff |
|----|--------------|------------------|---------------|----------|------|
| 1  |              |                  |               |          |      |
| 2  |              |                  |               |          |      |
| 3  |              |                  |               |          |      |
| 4  |              |                  |               |          |      |
| 5  |              |                  |               |          |      |

## Intentos fallidos y correcciones

| Qué pasó | Cómo se detectó | Cómo se resolvió |
|---|---|---|
| `.gitignore` creado con `Out-File` quedó con BOM y la regla `__pycache__/` no aplicaba | Revisión de los bytes del archivo (`od -c`) | Se reescribió sin BOM |

## Variaciones de prompts

*(Se llena conforme se comparan prompts.)*
