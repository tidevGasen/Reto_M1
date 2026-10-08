"""Pruebas de caracterizacion agregadas antes de refactorizar.

Fijan detalles observables que la suite original no cubre (texto del
ticket, mensajes de error, umbrales exactos, formato de reportes) para
detectar cualquier cambio de comportamiento durante la refactorizacion.
"""

import json

import pytest

import almacen
import gestor
import reportes


def test_ticket_sin_descuento_formato_exacto():
    gestor.agregarProducto("A1", "Café", 10.0, 50)
    venta = gestor.registrar_venta("A1", 2)
    assert venta["ticket"] == (
        "TIENDA LA ESQUINA\n"
        "----------------------------\n"
        "Folio: 1\n"
        "Café x2\n"
        "Subtotal: $20.0\n"
        "IVA: $3.2\n"
        "TOTAL: $23.2\n"
    )


def test_ticket_con_descuento_incluye_linea_descuento():
    gestor.agregarProducto("A1", "Café", 100.0, 50)
    venta = gestor.registrar_venta("A1", 6, "VIP007")
    assert venta["ticket"] == (
        "TIENDA LA ESQUINA\n"
        "----------------------------\n"
        "Folio: 1\n"
        "Café x6\n"
        "Subtotal: $600.0\n"
        "Descuento: -$42.0\n"
        "IVA: $89.28\n"
        "TOTAL: $647.28\n"
    )


def test_campos_de_la_venta():
    gestor.agregarProducto("A1", "Café", 100.0, 50)
    venta = gestor.registrar_venta("A1", 20, "C1")
    assert set(venta) == {
        "folio", "codigo", "nombre", "cantidad", "subtotal", "descuento",
        "impuesto", "total", "cliente", "fecha", "ticket",
    }
    assert venta["subtotal"] == 2000.0
    assert venta["descuento"] == 200.0
    assert venta["impuesto"] == 288.0
    assert venta["cliente"] == "C1"


@pytest.mark.parametrize(
    ("precio", "cantidad", "total"),
    [
        (499.99, 1, 579.99),  # justo debajo de 500: sin descuento
        (500.0, 1, 551.0),  # exactamente 500: 5 %
        (999.99, 1, 1101.99),  # justo debajo de 1000: 5 %
        (1000.0, 1, 1044.0),  # exactamente 1000: 10 %
    ],
)
def test_umbrales_de_descuento_por_volumen(precio, cantidad, total):
    gestor.agregarProducto("A1", "X", precio, 10)
    assert gestor.registrar_venta("A1", cantidad)["total"] == total
    gestor.reiniciar_sistema()
    gestor.agregarProducto("A1", "X", precio, 10)
    assert gestor.cotizar("A1", cantidad) == total


def test_vip_requiere_monto_estrictamente_mayor_a_200():
    gestor.agregarProducto("A1", "X", 100.0, 50)
    # subtotal 200, sin descuento: 200 > 200 es falso -> sin extra VIP
    assert gestor.registrar_venta("A1", 2, "VIP1")["descuento"] == 0
    # subtotal 300 -> extra 2 % = 6
    assert gestor.registrar_venta("A1", 3, "VIP1")["descuento"] == 6.0


def test_vip_solo_si_el_codigo_empieza_con_vip():
    gestor.agregarProducto("A1", "X", 100.0, 50)
    assert gestor.registrar_venta("A1", 3, "vip1")["descuento"] == 0
    assert gestor.registrar_venta("A1", 3, "VI")["descuento"] == 0
    assert gestor.registrar_venta("A1", 3, "XVIP")["descuento"] == 0


def test_cotizar_no_aplica_extra_vip_ni_registra_venta():
    gestor.agregarProducto("A1", "X", 100.0, 50)
    assert gestor.cotizar("A1", 6) == 661.2
    assert gestor.VENTAS == []
    assert gestor.INVENTARIO["A1"]["stock"] == 50


@pytest.mark.parametrize(
    ("codigo", "cantidad", "mensaje"),
    [
        ("", 1, "codigo vacio"),
        (None, 1, "codigo vacio"),
        ("ZZ", 1, "producto no existe"),
        ("ZZ", 0, "producto no existe"),  # producto se valida antes que cantidad
        ("A1", 0, "cantidad invalida"),
        ("A1", None, "cantidad invalida"),
        ("A1", 99, "stock insuficiente"),
    ],
)
def test_mensajes_de_error_de_registrar_venta(codigo, cantidad, mensaje):
    gestor.agregarProducto("A1", "X", 10.0, 5)
    assert gestor.registrar_venta(codigo, cantidad) is None
    assert gestor.ultimo_error == mensaje


def test_mensajes_de_error_de_cotizar():
    gestor.agregarProducto("A1", "X", 10.0, 5)
    assert gestor.cotizar("ZZ", 0) is None
    assert gestor.ultimo_error == "producto no existe"
    assert gestor.cotizar("A1", 0) is None
    assert gestor.ultimo_error == "cantidad invalida"


def test_mensajes_de_error_de_productos():
    gestor.agregarProducto("A1", "X", 10.0, 5)
    casos = [
        (lambda: gestor.agregarProducto("", "X", 1, 1), "codigo vacio"),
        (lambda: gestor.agregarProducto("A1", "X", 1, 1), "el producto ya existe"),
        (lambda: gestor.agregarProducto("A2", "X", 0, 1), "precio invalido"),
        (lambda: gestor.agregarProducto("A2", "X", 1, -1), "stock invalido"),
        (lambda: gestor.eliminar_producto("ZZ"), "producto no existe"),
        (lambda: gestor.actualizar_stock("ZZ", 1), "producto no existe"),
        (lambda: gestor.actualizar_stock("A1", -6), "el stock no puede quedar negativo"),
    ]
    for accion, mensaje in casos:
        assert accion() is False
        assert gestor.ultimo_error == mensaje


def test_reporte_inventario_formato_exacto(capsys):
    gestor.agregarProducto("A1", "Leche", 26.0, 3)
    gestor.agregarProducto("A2", "Azúcar", 32.5, 40)
    texto = reportes.reporte_inventario()
    assert texto == (
        "===== INVENTARIO =====\n"
        "A1 | Leche | $26.0 | stock: 3  <-- STOCK BAJO\n"
        "A2 | Azúcar | $32.5 | stock: 40\n"
        "Valor total del inventario: $1378.0\n"
    )
    assert capsys.readouterr().out == texto + "\n"


def test_resumen_ventas_formato_exacto(capsys):
    gestor.agregarProducto("A1", "Café", 10.0, 50)
    gestor.registrar_venta("A1", 2)
    gestor.registrar_venta("A1", 1)
    texto = reportes.resumen_ventas()
    assert texto == (
        "===== RESUMEN DE VENTAS =====\n"
        "Folio 1: Café x2 = $23.2\n"
        "Folio 2: Café x1 = $11.6\n"
        "Numero de ventas: 2\n"
        "Total del dia: $34.8\n"
    )
    assert capsys.readouterr().out == texto + "\n"


def test_stock_bajo_umbral_es_menor_que_5():
    gestor.agregarProducto("A1", "X", 1.0, 4)
    gestor.agregarProducto("A2", "Y", 1.0, 5)
    assert [p["codigo"] for p in reportes.productos_stock_bajo()] == ["A1"]


def test_mas_vendidos_por_defecto_regresa_3_y_respeta_empates():
    for codigo in ("A", "B", "C", "D"):
        gestor.agregarProducto(codigo, codigo, 1.0, 100)
    gestor.registrar_venta("A", 1)
    gestor.registrar_venta("B", 3)
    gestor.registrar_venta("C", 1)
    gestor.registrar_venta("D", 2)
    # empate A/C: se conserva el orden de primera venta (orden estable)
    assert reportes.mas_vendidos() == [("B", 3), ("D", 2), ("A", 1)]
    assert reportes.mas_vendidos(10)[-1] == ("C", 1)


def test_buscar_producto_conserva_orden_de_alta():
    gestor.agregarProducto("B", "pan dulce", 1.0, 1)
    gestor.agregarProducto("A", "Pan blanco", 1.0, 1)
    assert [p["codigo"] for p in gestor.buscarProducto("PAN")] == ["B", "A"]


def test_cargar_archivo_corrupto(tmp_path):
    ruta = tmp_path / "malo.json"
    ruta.write_text("{no es json", encoding="utf-8")
    assert almacen.cargar_datos(str(ruta)) is False
    assert gestor.ultimo_error == "archivo corrupto"


def test_cargar_archivo_inexistente_deja_mensaje(tmp_path):
    assert almacen.cargar_datos(str(tmp_path / "x.json")) is False
    assert gestor.ultimo_error == "el archivo no existe"


def test_guardar_datos_estructura_del_json(tmp_path):
    ruta = tmp_path / "d.json"
    gestor.agregarProducto("A1", "Café", 10.0, 5)
    gestor.registrar_venta("A1", 1)
    assert almacen.guardar_datos(str(ruta)) is True
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert set(datos) == {"inventario", "ventas", "contador"}
    assert datos["contador"] == 1
    assert "Café" in ruta.read_text(encoding="utf-8")  # ensure_ascii=False


def test_cargar_sin_contador_reinicia_folio(tmp_path):
    ruta = tmp_path / "d.json"
    ruta.write_text('{"inventario": {}, "ventas": []}', encoding="utf-8")
    gestor.agregarProducto("A1", "X", 1.0, 5)
    gestor.registrar_venta("A1", 1)
    assert almacen.cargar_datos(str(ruta)) is True
    gestor.agregarProducto("A1", "X", 1.0, 5)
    assert gestor.registrar_venta("A1", 1)["folio"] == 1


def test_reiniciar_sistema_conserva_los_mismos_objetos():
    inventario, ventas = gestor.INVENTARIO, gestor.VENTAS
    gestor.agregarProducto("A1", "X", 1.0, 5)
    gestor.reiniciar_sistema()
    assert gestor.INVENTARIO is inventario
    assert gestor.VENTAS is ventas
