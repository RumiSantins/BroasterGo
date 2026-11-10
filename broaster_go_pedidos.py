# ==========================================
# BROASTER GO - Pedidos con control de stock
# Modelo IPO: ENTRADAS -> PROCESO -> SALIDAS
# ==========================================

# ==========================================
# REGLAS DE NEGOCIO (valores del README, sección 6.1)
# ==========================================
STOCK_MINIMO = 3                                      # R8: alerta si quedan 3 unidades o menos
PEDIDO_MINIMO_DELIVERY = 25.0                         # R4: monto mínimo para envío a domicilio
TARIFAS_DELIVERY = {"A": 3.0, "B": 5.0, "C": 8.0}     # R5: costo de envío según la zona
CUPONES = {"BROASTER10": 10, "FAMILIA15": 15}         # R6: código del cupón -> % de descuento
FORMAS_PAGO = ["Efectivo", "Yape", "Plin", "Tarjeta"]  # R7: formas de pago aceptadas


# ==========================================
# DEFINICIÓN DE ESTRUCTURAS DE DATOS (CLASES)
# ==========================================
class Cliente:
    def __init__(self, codigo: str, nombre: str, correo: str):
        self.codigo = codigo
        self.nombre = nombre
        self.correo = correo


class Producto:
    def __init__(self, codigo: str, nombre: str, precio: float, stock: int):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock


def crear_menu() -> dict:
    """Catálogo inicial de productos (código -> Producto)."""
    return {
        "P001": Producto("P001", "Pieza de Pollo Broaster", precio=8.5, stock=10),
        "P002": Producto("P002", "Combo 2 Piezas + Papas", precio=18.0, stock=5),
        "P003": Producto("P003", "Papas Fritas", precio=6.0, stock=15),
        "P004": Producto("P004", "Gaseosa 500ml", precio=4.0, stock=20),
    }


# ==========================================
# VALIDACIONES DE LAS ENTRADAS
# ==========================================
def validar_correo(correo: str) -> bool:
    """Revisión sencilla: una sola @, texto antes de la @ y un punto en el dominio.
    'ana@gmail.com' -> True | 'ana.gmail.com' -> False | 'ana@gmail' -> False
    """
    if " " in correo or correo.count("@") != 1:
        return False
    usuario, dominio = correo.split("@")
    if usuario == "" or "." not in dominio:
        return False
    if dominio.startswith(".") or dominio.endswith("."):
        return False
    return True


def validar_cliente(cliente: Cliente) -> list[str]:
    """Devuelve la lista de problemas encontrados (lista vacía = cliente correcto)."""
    problemas = []
    if cliente.codigo == "":
        problemas.append("El código del cliente es obligatorio.")
    if cliente.nombre == "":
        problemas.append("El nombre del cliente es obligatorio.")
    if not validar_correo(cliente.correo):
        problemas.append(f"El correo '{cliente.correo}' no es válido (ejemplo: ana@gmail.com).")
    return problemas


# ==========================================
# PROCESO (LÓGICA DE TRANSFORMACIÓN)
# ==========================================
class SistemaPedidos:
    """PROCESO: Recibe las entradas, aplica las reglas de negocio (validaciones/cálculos) y genera el resultado."""

    @staticmethod
    def procesar_pedido(
        cliente: Cliente,
        items_solicitados: list[tuple[Producto, int]],
        zona: str | None = None,   # None = recojo en local; "A", "B" o "C" = delivery
        cupon: str = "",
        forma_pago: str = "Efectivo",
    ) -> dict:
        items_confirmados = []
        errores = []
        subtotal = 0.0

        # PROCESO 1: Validación de cada ítem (R1, R2, R3) y separación del stock
        for producto, cantidad in items_solicitados:
            if cantidad <= 0:
                errores.append(f"Cantidad inválida ({cantidad}) para {producto.nombre}")
                continue
            if producto.precio <= 0:
                errores.append(f"Precio inválido para {producto.nombre}")
                continue
            if producto.stock < cantidad:
                errores.append(
                    f"Sin stock suficiente para {producto.nombre} (Disponible: {producto.stock})"
                )
                continue

            producto.stock -= cantidad
            importe = producto.precio * cantidad
            subtotal += importe
            items_confirmados.append((producto, cantidad, importe))

        # PROCESO 2: Reglas del pedido completo
        pedido_valido = True

        if len(items_confirmados) == 0:
            errores.append("El pedido no tiene productos válidos.")
            pedido_valido = False

        if forma_pago not in FORMAS_PAGO:                        # R7
            errores.append(f"Forma de pago no aceptada: {forma_pago}")
            pedido_valido = False

        costo_delivery = 0.0
        if zona is not None:
            zona = zona.upper()
        if zona is not None and len(items_confirmados) > 0:
            if zona not in TARIFAS_DELIVERY:                     # R5
                errores.append(f"La zona '{zona}' no tiene cobertura de delivery.")
                pedido_valido = False
            elif subtotal < PEDIDO_MINIMO_DELIVERY:              # R4
                errores.append(
                    f"Para delivery el pedido mínimo es S/ {PEDIDO_MINIMO_DELIVERY:.2f} "
                    f"(este pedido suma S/ {subtotal:.2f})."
                )
                pedido_valido = False
            else:
                costo_delivery = TARIFAS_DELIVERY[zona]

        # Si el pedido se rechaza, devolvemos el stock que habíamos separado
        if not pedido_valido:
            for producto, cantidad, _ in items_confirmados:
                producto.stock += cantidad
            items_confirmados = []
            subtotal = 0.0
            costo_delivery = 0.0

        # PROCESO 3: Cupón de descuento (R6)
        porcentaje = 0
        cupon = cupon.strip().upper()
        if pedido_valido and cupon != "":
            if cupon in CUPONES:
                porcentaje = CUPONES[cupon]
            else:
                errores.append(f"El cupón '{cupon}' no existe; no se aplicó descuento.")
        descuento = round(subtotal * porcentaje / 100, 2)
        total = round(subtotal - descuento + costo_delivery, 2)

        # PROCESO 4: Alerta de stock mínimo (R8)
        alertas_stock = []
        for producto, _, _ in items_confirmados:
            if producto.stock <= STOCK_MINIMO:
                aviso = f"{producto.nombre}: solo quedan {producto.stock}"
                if aviso not in alertas_stock:  # por si el producto se pidió dos veces
                    alertas_stock.append(aviso)

        # ESTRUCTURACIÓN DE LAS SALIDAS
        return {
            "cliente": cliente.nombre,
            "codigo": cliente.codigo,
            "correo": cliente.correo,
            "estado": "Confirmado" if pedido_valido else "Rechazado",
            "items_confirmados": [
                f"{p.nombre} x{cant} - S/ {imp:.2f}"
                for p, cant, imp in items_confirmados
            ],
            "pedidos_cocina": [(p.nombre, cant) for p, cant, _ in items_confirmados],
            "subtotal": round(subtotal, 2),
            "cupon": cupon if porcentaje > 0 else "",
            "porcentaje_descuento": porcentaje,
            "descuento": descuento,
            "zona": zona,
            "delivery": costo_delivery,
            "forma_pago": forma_pago,
            "total": total,
            "observaciones": errores,
            "alertas_stock": alertas_stock,
        }


def calcular_cierre_caja(pedidos_del_dia: list[dict]) -> dict:
    """Suma las ventas del día (solo pedidos confirmados) y las agrupa por forma de pago."""
    confirmados = 0
    rechazados = 0
    total_vendido = 0.0
    por_forma_pago = {}
    for forma in FORMAS_PAGO:
        por_forma_pago[forma] = 0.0

    for pedido in pedidos_del_dia:
        if pedido["estado"] != "Confirmado":
            rechazados += 1
            continue
        confirmados += 1
        total_vendido += pedido["total"]
        por_forma_pago[pedido["forma_pago"]] += pedido["total"]

    return {
        "confirmados": confirmados,
        "rechazados": rechazados,
        "total_vendido": round(total_vendido, 2),
        "por_forma_pago": por_forma_pago,
    }


# ==========================================
# 1. ENTRADAS (INPUTS) - lectura por teclado
# ==========================================
def pedir_si_no(mensaje: str) -> bool:
    while True:
        respuesta = input(mensaje).strip().upper()
        if respuesta in ("S", "N"):
            return respuesta == "S"
        print(" Responde S (sí) o N (no).")


def pedir_cliente() -> Cliente:
    """ENTRADA 1: datos del cliente. Repite hasta que sean válidos."""
    while True:
        cliente = Cliente(
            codigo=input("Código del cliente: ").strip(),
            nombre=input("Nombre del cliente: ").strip(),
            correo=input("Correo del cliente: ").strip(),
        )
        problemas = validar_cliente(cliente)
        if len(problemas) == 0:
            return cliente
        for problema in problemas:
            print(f" {problema}")
        print(" Vuelve a ingresar los datos del cliente.\n")


def mostrar_menu(menu_productos: dict):
    print("\n--- Menú disponible ---")
    for p in menu_productos.values():
        aviso = "  (AGOTADO)" if p.stock == 0 else ""
        print(f"{p.codigo} - {p.nombre} - S/ {p.precio:.2f} - Stock: {p.stock}{aviso}")


def pedir_productos(menu_productos: dict) -> list:
    """ENTRADA 2: productos y cantidades."""
    solicitud_pedido = []
    print("\nIngresa los productos del pedido. Escribe 'fin' para terminar.")

    while True:
        codigo_producto = input("\nCódigo de producto: ").strip().upper()
        if codigo_producto == "FIN":
            break

        producto = menu_productos.get(codigo_producto)
        if producto is None:
            print(" Código no válido, intenta de nuevo.")
            continue

        try:
            cantidad = int(input(f"Cantidad de '{producto.nombre}': "))
            if cantidad <= 0:
                print(" La cantidad debe ser mayor a 0.")
                continue
        except ValueError:
            print(" Ingresa un número entero válido.")
            continue

        solicitud_pedido.append((producto, cantidad))

    return solicitud_pedido


def pedir_zona():
    """ENTRADA 3: tipo de entrega. Devuelve None (recojo en local) o la zona A/B/C."""
    if not pedir_si_no("\n¿Es para delivery? (S/N): "):
        return None
    print(f"Zonas (pedido mínimo S/ {PEDIDO_MINIMO_DELIVERY:.2f}):")
    for zona, tarifa in TARIFAS_DELIVERY.items():
        print(f" Zona {zona}: S/ {tarifa:.2f}")
    while True:
        zona = input("Zona: ").strip().upper()
        if zona in TARIFAS_DELIVERY:
            return zona
        print(" Zona no válida. Escribe A, B o C.")


def pedir_forma_pago() -> str:
    """ENTRADA 4: forma de pago."""
    print("\nFormas de pago:")
    for numero, forma in enumerate(FORMAS_PAGO, start=1):
        print(f" {numero}. {forma}")
    while True:
        opcion = input("Elige una opción: ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(FORMAS_PAGO):
            return FORMAS_PAGO[int(opcion) - 1]
        print(f" Escribe un número del 1 al {len(FORMAS_PAGO)}.")


# ==========================================
# 3. SALIDAS (OUTPUTS) - documentos
# ==========================================
def emitir_boleta(resultado: dict, numero: int):
    """SALIDA 1: boleta de venta."""
    print("\n==========================================")
    print(f"=== BOLETA N.º {numero:04d} - BROASTER GO ===")
    print("==========================================")
    print(f"Cliente: {resultado['cliente']} ({resultado['codigo']})")

    if resultado["estado"] == "Rechazado":
        print("\n PEDIDO RECHAZADO (no se descontó stock)")
        return

    print("\n Productos Confirmados:")
    for item in resultado["items_confirmados"]:
        print(f" - {item}")

    print(f"\n Subtotal:  S/ {resultado['subtotal']:.2f}")
    if resultado["descuento"] > 0:
        print(f" Descuento: -S/ {resultado['descuento']:.2f} "
              f"(cupón {resultado['cupon']}, {resultado['porcentaje_descuento']}%)")
    if resultado["zona"] is not None:
        print(f" Delivery:  S/ {resultado['delivery']:.2f} (zona {resultado['zona']})")
    else:
        print(" Entrega:   recojo en local")
    print(f" Total a pagar: S/ {resultado['total']:.2f}  ({resultado['forma_pago']})")


def notificar_cliente(resultado: dict):
    """SALIDA 2: notificación al cliente."""
    print("\n Notificación de confirmación:")
    print(f" Enviado a: {resultado['correo']}")


def enviar_comanda(resultado: dict):
    """SALIDA 3: comanda para la cocina."""
    print("\n Pedido enviado al Panel de Cocina:")
    for nombre, cantidad in resultado["pedidos_cocina"]:
        print(f" - {cantidad} x {nombre}")


def mostrar_incidencias(resultado: dict):
    """SALIDA 4: observaciones y alertas de stock."""
    if resultado["observaciones"]:
        print("\n Observaciones/Errores durante el proceso:")
        for err in resultado["observaciones"]:
            print(f" - {err}")
    if resultado["alertas_stock"]:
        print("\n ALERTA de stock mínimo (reponer pronto):")
        for alerta in resultado["alertas_stock"]:
            print(f" - {alerta}")


def mostrar_cierre_caja(pedidos_del_dia: list[dict], menu_productos: dict):
    """SALIDA 5: resumen del día."""
    cierre = calcular_cierre_caja(pedidos_del_dia)
    print("\n==========================================")
    print("=== CIERRE DE CAJA - BROASTER GO ===")
    print("==========================================")
    print(f"Pedidos confirmados: {cierre['confirmados']}")
    print(f"Pedidos rechazados:  {cierre['rechazados']}")
    print(f"Total vendido:       S/ {cierre['total_vendido']:.2f}")
    print("\nVentas por forma de pago:")
    for forma, monto in cierre["por_forma_pago"].items():
        print(f" - {forma}: S/ {monto:.2f}")
    print("\nStock final:")
    for p in menu_productos.values():
        print(f" - {p.nombre}: {p.stock}")


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================
def main():
    menu_productos = crear_menu()
    pedidos_del_dia = []

    while True:
        print("\n=== BROASTER GO - Nuevo Pedido ===")

        # 1. ENTRADAS
        cliente = pedir_cliente()
        mostrar_menu(menu_productos)
        solicitud_pedido = pedir_productos(menu_productos)
        zona = pedir_zona()
        cupon = input("\nCupón de descuento (Enter si no tiene): ")
        forma_pago = pedir_forma_pago()

        # 2. PROCESO
        resultado = SistemaPedidos.procesar_pedido(cliente, solicitud_pedido, zona, cupon, forma_pago)
        pedidos_del_dia.append(resultado)

        # 3. SALIDAS
        emitir_boleta(resultado, numero=len(pedidos_del_dia))
        if resultado["estado"] == "Confirmado":
            notificar_cliente(resultado)
            enviar_comanda(resultado)
        mostrar_incidencias(resultado)

        if not pedir_si_no("\n¿Registrar otro pedido? (S/N): "):
            break

    mostrar_cierre_caja(pedidos_del_dia, menu_productos)


# solo se ejecuta si corremos este archivo directamente (no cuando lo importan las pruebas)
if __name__ == "__main__":
    main()
