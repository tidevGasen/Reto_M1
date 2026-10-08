"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"


def pedir_numero(mensaje):
    """Pide un numero al usuario hasta que escriba algo valido."""
    while True:
        respuesta = input(mensaje)
        try:
            return float(respuesta)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def mostrar_error():
    print("Error:", gestor.ultimo_error)


def agregar_producto():
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        mostrar_error()


def registrar_venta():
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        mostrar_error()


def cotizar():
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        mostrar_error()


def mostrar_mas_vendidos():
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def mostrar_stock_bajo():
    bajos = reportes.productos_stock_bajo()
    if not bajos:
        print("No hay productos con stock bajo.")
    for producto in bajos:
        print("OJO:", producto["nombre"], "solo tiene", producto["stock"], "unidades")


def guardar_y_salir():
    """Guarda los datos y regresa True para terminar el menu."""
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")
    return True


# Cada opcion: tecla -> (etiqueta mostrada, funcion que la atiende).
# Una funcion que regresa True termina el menu.
OPCIONES = {
    "1": ("Agregar producto", agregar_producto),
    "2": ("Registrar venta", registrar_venta),
    "3": ("Cotizar", cotizar),
    "4": ("Reporte de inventario", reportes.reporte_inventario),
    "5": ("Resumen de ventas", reportes.resumen_ventas),
    "6": ("Mas vendidos", mostrar_mas_vendidos),
    "7": ("Alertas de stock bajo", mostrar_stock_bajo),
    "8": ("Guardar y salir", guardar_y_salir),
}


def cargar_datos_iniciales():
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)


def mostrar_opciones():
    print("")
    for tecla, (etiqueta, _) in OPCIONES.items():
        print(f"{tecla}) {etiqueta}")


def menu():
    """Ciclo principal: muestra el menu y despacha la opcion elegida."""
    print("Bienvenido al gestor de la tienda La Esquina")
    cargar_datos_iniciales()
    while True:
        mostrar_opciones()
        opcion = OPCIONES.get(input("Opcion: "))
        if opcion is None:
            print("Opcion no valida.")
            continue
        _, accion = opcion
        if accion() is True:
            break


if __name__ == "__main__":
    menu()
