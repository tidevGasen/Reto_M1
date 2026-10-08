"""Persistencia del gestor: carga y guardado de datos en JSON."""

import json
import os
import tempfile

import gestor


def guardar_datos(ruta: str) -> bool:
    """Guarda el inventario, las ventas y el folio actual en un JSON.

    Escribe primero en un temporal de la misma carpeta y luego lo
    reemplaza de forma atomica: si el proceso se interrumpe a la mitad,
    el archivo anterior queda intacto en lugar de quedar corrupto.
    """
    datos = {
        "inventario": gestor.INVENTARIO,
        "ventas": gestor.VENTAS,
        "contador": gestor.contador_ventas,
    }
    carpeta = os.path.dirname(os.path.abspath(ruta))
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=carpeta, suffix=".tmp", delete=False
    ) as archivo:
        temporal = archivo.name
        try:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)
        except BaseException:
            archivo.close()
            os.remove(temporal)
            raise
    os.replace(temporal, ruta)
    return True


def cargar_datos(ruta: str) -> bool:
    """Lee el archivo JSON y deja los datos en el estado global.

    Regresa False si el archivo no existe o esta corrupto (no es JSON
    valido o no esta en UTF-8).
    """
    if not os.path.exists(ruta):
        gestor.ultimo_error = "el archivo no existe"
        return False
    try:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (json.JSONDecodeError, UnicodeDecodeError):
        gestor.ultimo_error = "archivo corrupto"
        return False
    gestor.INVENTARIO.clear()
    gestor.INVENTARIO.update(datos["inventario"])
    gestor.VENTAS.clear()
    gestor.VENTAS.extend(datos["ventas"])
    gestor.contador_ventas = datos.get("contador", 0)
    return True


def hay_archivo(ruta: str) -> bool:
    """Indica si ya existe el archivo de datos."""
    return os.path.exists(ruta)
