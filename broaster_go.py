# Broaster GO - sistema de pedidos en el mostrador
# Traduccion a Python del algoritmo hecho en PSeInt

from calculos import CARTA, IGV, calcular_totales, soles


def mostrar_carta():
    print()
    print("==== Bienvenido a Broaster GO ====")
    for codigo in CARTA:
        nombre, precio = CARTA[codigo]
        print(str(codigo) + ". " + nombre.ljust(16) + " " + soles(precio))
    print("0. Finalizar pedido")


def pedir_entero(mensaje):
    # repite la pregunta hasta que el usuario escriba un numero entero
    while True:
        texto = input(mensaje)
        try:
            return int(texto)
        except ValueError:
            print("Eso no es un numero entero. Intente de nuevo.")


def pedir_porcentaje(mensaje):
    # repite la pregunta hasta que el usuario escriba un numero entre 0 y 100
    while True:
        texto = input(mensaje)
        try:
            porcentaje = float(texto)
        except ValueError:
            print("Eso no es un numero. Intente de nuevo.")
            continue

        if 0 <= porcentaje <= 100:
            return porcentaje
        print("El porcentaje debe estar entre 0 y 100.")


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
        print(nombre + " x" + str(cantidad) + " agregado. Subtotal actual: " + soles(subtotal))

    if len(pedido) == 0:
        print("No se registro ningun articulo. Hasta luego.")
        return

    # cupon de descuento
    porcentaje = 0.0
    respuesta = input("Desea aplicar cupon de descuento? (S/N): ").strip().upper()
    if respuesta == "S":
        porcentaje = pedir_porcentaje("Ingrese porcentaje de descuento: ")

    # las cuentas (descuento -> IGV -> total) se hacen en calculos.py
    totales = calcular_totales(subtotal, porcentaje)

    print()
    print("=== Resumen del pedido ===")
    for nombre, cantidad, importe in pedido:
        print(str(cantidad) + " x " + nombre.ljust(16) + " " + soles(importe))
    print("-" * 32)
    print("Subtotal:        " + soles(totales["subtotal"]))
    print("Descuento:      -" + soles(totales["descuento"]) + "  (" + format(totales["porcentaje"], "g") + "%)")
    print("IGV (" + format(IGV * 100, "g") + "%):       " + soles(totales["igv"]))
    print("TOTAL A PAGAR:   " + soles(totales["total"]))
    print("Gracias por elegir Broaster GO. Vuelva pronto!")


# solo se ejecuta si corremos este archivo directamente (no cuando otro archivo lo importa)
if __name__ == "__main__":
    main()
