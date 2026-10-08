"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Contiene la logica de negocio y el estado global de la aplicacion.
"""

from datetime import datetime

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contadorVentas = 0
ultimo_error = ""

# ---------------------------------------------------------------
# Reglas de negocio de precios
# ---------------------------------------------------------------
TASA_IVA = 0.16
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200  # sobre subtotal - descuento, estrictamente mayor
TASA_EXTRA_VIP = 0.02  # se aplica sobre el subtotal


def reiniciar_sistema():
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contadorVentas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contadorVentas = 0
    ultimo_error = ""


def agregarProducto(codigo, nombre, precio, stock):
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    x = {}
    x["codigo"] = codigo
    x["nombre"] = nombre
    x["precio"] = precio
    x["stock"] = stock
    INVENTARIO[codigo] = x
    return True


def eliminar_producto(codigo):
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo, cantidad):
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    aux = INVENTARIO[codigo]["stock"] + cantidad
    if aux < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = aux
    return True


def buscarProducto(texto):
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    texto = texto.lower()
    return [p for p in INVENTARIO.values() if texto in p["nombre"].lower()]


def _validar_venta(codigo, cantidad):
    """Regresa el mensaje de error de la venta, o None si es valida."""
    if codigo is None or codigo == "":
        return "codigo vacio"
    if codigo not in INVENTARIO:
        return "producto no existe"
    if cantidad is None or cantidad <= 0:
        return "cantidad invalida"
    if INVENTARIO[codigo]["stock"] < cantidad:
        return "stock insuficiente"
    return None


def _descuento_por_volumen(subtotal):
    """Descuento escalonado segun el monto de la compra."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def _es_vip(cliente):
    return bool(cliente) and cliente.startswith(PREFIJO_VIP)


def calcular_importes(subtotal, cliente=""):
    """Calcula (descuento, impuesto, total) de una compra.

    Los clientes VIP reciben un extra sobre el subtotal si la compra,
    ya con el descuento por volumen, supera MONTO_MINIMO_VIP.
    """
    descuento = _descuento_por_volumen(subtotal)
    if _es_vip(cliente) and subtotal - descuento > MONTO_MINIMO_VIP:
        descuento = descuento + subtotal * TASA_EXTRA_VIP
    base = subtotal - descuento
    impuesto = base * TASA_IVA
    return descuento, impuesto, round(base + impuesto, 2)


def _armar_ticket(venta, con_descuento):
    """Arma el ticket en texto plano a partir de una venta registrada."""
    lineas = [
        "TIENDA LA ESQUINA",
        "----------------------------",
        f"Folio: {venta['folio']}",
        f"{venta['nombre']} x{venta['cantidad']}",
        f"Subtotal: ${venta['subtotal']}",
    ]
    if con_descuento:
        lineas.append(f"Descuento: -${venta['descuento']}")
    lineas.append(f"IVA: ${venta['impuesto']}")
    lineas.append(f"TOTAL: ${venta['total']}")
    return "\n".join(lineas) + "\n"


def registrar_venta(codigo, cantidad, cliente=""):
    """Registra una venta: valida, calcula importes, descuenta stock y
    genera folio y ticket. Si algo falla regresa None y deja el motivo
    en ultimo_error.
    """
    global contadorVentas, ultimo_error
    error = _validar_venta(codigo, cantidad)
    if error is not None:
        ultimo_error = error
        return None
    producto = INVENTARIO[codigo]
    subtotal = producto["precio"] * cantidad
    descuento, impuesto, total = calcular_importes(subtotal, cliente)
    producto["stock"] = producto["stock"] - cantidad
    contadorVentas = contadorVentas + 1
    venta = {
        "folio": contadorVentas,
        "codigo": codigo,
        "nombre": producto["nombre"],
        "cantidad": cantidad,
        "subtotal": round(subtotal, 2),
        "descuento": round(descuento, 2),
        "impuesto": round(impuesto, 2),
        "total": total,
        "cliente": cliente,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    venta["ticket"] = _armar_ticket(venta, con_descuento=descuento > 0)
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta.

    No aplica el extra VIP porque la cotizacion no recibe cliente.
    """
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    _, _, total = calcular_importes(INVENTARIO[codigo]["precio"] * cantidad)
    return total
