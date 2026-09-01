# Broaster GO - sistema de pedidos en el mostrador
# Traduccion a Python del algoritmo hecho en PSeInt

IGV = 0.18  # 18% en Peru

# codigo de opcion -> (nombre del articulo, precio)
CARTA = {
    1: ("Combo Zinger", 60.0),
    2: ("Combo 3 piezas", 40.0),
    3: ("Combo familiar", 90.0),
    4: ("Bebida", 7.0),
    5: ("Papas", 15.0),
}


def mostrar_carta():
    print()
    print("==== Bienvenido a Broaster GO ====")
    for codigo in CARTA:
        nombre, precio = CARTA[codigo]
        print(str(codigo) + ". " + nombre.ljust(16) + " S/ " + format(precio, ".2f"))
    print("0. Finalizar pedido")


def pedir_entero(mensaje):
    # repite la pregunta hasta que el usuario escriba un numero entero
    while True:
        texto = input(mensaje)
        try:
            return int(texto)
        except ValueError:
            print("Eso no es un numero entero. Intente de nuevo.")


def pedir_decimal(mensaje):
    while True:
        texto = input(mensaje)
        try:
            return float(texto)
        except ValueError:
            print("Eso no es un numero. Intente de nuevo.")


def main():
    pedido = []      # lista de (nombre, cantidad, importe)
    subtotal = 0.0

    # el menu se repite hasta que el usuario escriba 0
    while True:
        mostrar_carta()
        opcion = pedir_entero("Ingrese opcion: ")

        if opcion == 0:
            break

        if opcion not in CARTA:
            print("Opcion no valida. Intente de nuevo.")
            continue

        nombre, precio = CARTA[opcion]
        cantidad = pedir_entero("Cantidad: ")

        if cantidad <= 0:
            print("La cantidad debe ser mayor que cero.")
            continue

        importe = precio * cantidad   # en el PSeInt decia precio + cantidad
        subtotal = subtotal + importe
        pedido.append((nombre, cantidad, importe))
        print(nombre + " x" + str(cantidad) + " agregado. Subtotal actual: S/ " + format(subtotal, ".2f"))

    if len(pedido) == 0:
        print("No se registro ningun articulo. Hasta luego.")
        return

    # cupon de descuento
    monto_descuento = 0.0
    respuesta = input("Desea aplicar cupon de descuento? (S/N): ").strip().upper()

    if respuesta == "S":
        porcentaje = pedir_decimal("Ingrese porcentaje de descuento: ")
        if porcentaje < 0:
            porcentaje = 0.0
        if porcentaje > 100:
            porcentaje = 100.0
        monto_descuento = subtotal * (porcentaje / 100)

    impuesto = subtotal * IGV
    total = subtotal + impuesto - monto_descuento

    print()
    print("=== Resumen del pedido ===")
    for nombre, cantidad, importe in pedido:
        print(str(cantidad) + " x " + nombre.ljust(16) + " S/ " + format(importe, ".2f"))
    print("-" * 32)
    print("Subtotal:       S/ " + format(subtotal, ".2f"))
    print("IGV (18%):      S/ " + format(impuesto, ".2f"))
    print("Descuento:     -S/ " + format(monto_descuento, ".2f"))
    print("TOTAL A PAGAR:  S/ " + format(total, ".2f"))
    print("Gracias por elegir Broaster GO. Vuelva pronto!")


main()
