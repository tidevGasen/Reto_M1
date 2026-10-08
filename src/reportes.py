"""Reportes de la tienda: inventario, ventas y mas vendidos."""

import gestor
from gestor import Producto

STOCK_MINIMO = 5  # por debajo de este stock se considera "stock bajo"


def formatear_dinero(monto: float) -> str:
    """Da formato de dinero: $ seguido del monto redondeado a 2 decimales."""
    return "$" + str(round(monto, 2))


def productos_stock_bajo() -> list[Producto]:
    """Regresa la lista de productos con stock por debajo del minimo."""
    return [
        producto
        for producto in gestor.INVENTARIO.values()
        if producto["stock"] < STOCK_MINIMO
    ]


def reporte_inventario() -> str:
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    lineas = ["===== INVENTARIO ====="]
    for producto in gestor.INVENTARIO.values():
        linea = (
            f"{producto['codigo']} | {producto['nombre']}"
            f" | {formatear_dinero(producto['precio'])} | stock: {producto['stock']}"
        )
        if producto["stock"] < STOCK_MINIMO:
            linea += "  <-- STOCK BAJO"
        lineas.append(linea)
    productos = gestor.INVENTARIO.values()
    valor = sum(producto["precio"] * producto["stock"] for producto in productos)
    lineas.append(f"Valor total del inventario: {formatear_dinero(valor)}")
    texto = "\n".join(lineas) + "\n"
    print(texto)
    return texto


def total_vendido() -> float:
    """Suma el total (con IVA) de todas las ventas registradas."""
    return round(sum(venta["total"] for venta in gestor.VENTAS), 2)


def mas_vendidos(n: int = 3) -> list[tuple[str, int]]:
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    unidades: dict[str, int] = {}
    for venta in gestor.VENTAS:
        codigo = venta["codigo"]
        unidades[codigo] = unidades.get(codigo, 0) + venta["cantidad"]
    # sorted es estable: en empate conserva el orden de primera venta
    return sorted(unidades.items(), key=lambda par: par[1], reverse=True)[:n]


def resumen_ventas() -> str:
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    lineas = ["===== RESUMEN DE VENTAS ====="]
    for venta in gestor.VENTAS:
        lineas.append(
            f"Folio {venta['folio']}: {venta['nombre']} x{venta['cantidad']}"
            f" = {formatear_dinero(venta['total'])}"
        )
    total = sum(venta["total"] for venta in gestor.VENTAS)
    lineas.append(f"Numero de ventas: {len(gestor.VENTAS)}")
    lineas.append(f"Total del dia: {formatear_dinero(total)}")
    texto = "\n".join(lineas) + "\n"
    print(texto)
    return texto

