"""Reportes de la tienda: inventario, ventas y mas vendidos."""


import gestor


def hacer_cosa(v):
    # le da formato de dinero al numero
    return "$" + str(round(v, 2))


def productos_stock_bajo():
    """Regresa la lista de productos con stock por debajo del minimo."""
    return [p for p in gestor.INVENTARIO.values() if p["stock"] < 5]


def reporte_inventario():
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    lineas = ["===== INVENTARIO ====="]
    for p in gestor.INVENTARIO.values():
        linea = (
            f"{p['codigo']} | {p['nombre']} | {hacer_cosa(p['precio'])}"
            f" | stock: {p['stock']}"
        )
        if p["stock"] < 5:
            linea += "  <-- STOCK BAJO"
        lineas.append(linea)
    valor = sum(p["precio"] * p["stock"] for p in gestor.INVENTARIO.values())
    lineas.append(f"Valor total del inventario: {hacer_cosa(valor)}")
    s = "\n".join(lineas) + "\n"
    print(s)
    return s


def total_vendido():
    """Suma el total (con IVA) de todas las ventas registradas."""
    return round(sum(v["total"] for v in gestor.VENTAS), 2)


def mas_vendidos(n=3):
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    unidades = {}
    for v in gestor.VENTAS:
        unidades[v["codigo"]] = unidades.get(v["codigo"], 0) + v["cantidad"]
    # sorted es estable: en empate conserva el orden de primera venta
    return sorted(unidades.items(), key=lambda par: par[1], reverse=True)[:n]


def resumen_ventas():
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    lineas = ["===== RESUMEN DE VENTAS ====="]
    for v in gestor.VENTAS:
        lineas.append(
            f"Folio {v['folio']}: {v['nombre']} x{v['cantidad']}"
            f" = {hacer_cosa(v['total'])}"
        )
    total = sum(v["total"] for v in gestor.VENTAS)
    lineas.append(f"Numero de ventas: {len(gestor.VENTAS)}")
    lineas.append(f"Total del dia: {hacer_cosa(total)}")
    s = "\n".join(lineas) + "\n"
    print(s)
    return s

