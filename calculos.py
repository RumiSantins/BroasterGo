# Broaster GO - carta y calculos compartidos
# Este archivo lo usan broaster_go.py (consola) y broaster_go_gui.py (ventana).
# Antes cada programa tenia su propia copia de la carta y del IGV; ahora estan
# en un solo lugar: si cambia un precio, se cambia aqui y listo.

IGV = 0.18  # 18% en Peru

# codigo de opcion -> (nombre del articulo, precio)
CARTA = {
    1: ("Combo Zinger", 60.0),
    2: ("Combo 3 piezas", 40.0),
    3: ("Combo familiar", 90.0),
    4: ("Bebida", 7.0),
    5: ("Papas", 15.0),
}


def limitar_porcentaje(porcentaje):
    """Deja el porcentaje entre 0 y 100 (no existen descuentos negativos ni mayores al 100%)."""
    if porcentaje < 0:
        return 0.0
    if porcentaje > 100:
        return 100.0
    return porcentaje


def calcular_totales(subtotal, porcentaje_descuento):
    """Calcula descuento, IGV y total de un pedido.

    Orden correcto: primero se resta el descuento y DESPUES se calcula el IGV
    sobre lo que el cliente realmente paga.
    Ejemplo: subtotal 100 y cupon 10% -> descuento 10, IGV 16.20, total 106.20
    """
    porcentaje = limitar_porcentaje(porcentaje_descuento)
    descuento = round(subtotal * porcentaje / 100, 2)
    base = subtotal - descuento          # lo que se cobra antes de impuestos
    impuesto = round(base * IGV, 2)
    total = round(base + impuesto, 2)

    return {
        "subtotal": round(subtotal, 2),
        "porcentaje": porcentaje,
        "descuento": descuento,
        "igv": impuesto,
        "total": total,
    }


def soles(monto):
    """Da formato de dinero: 12.5 -> 'S/ 12.50'"""
    return "S/ " + format(monto, ".2f")
