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


# ==========================================
# PROCESO (LÓGICA DE TRANSFORMACIÓN)
# ==========================================
class SistemaPedidos:
    """PROCESO: Recibe las entradas, aplica las reglas de negocio (validaciones/cálculos) y genera el resultado."""

    @staticmethod
    def procesar_pedido(cliente: Cliente, items_solicitados: list[tuple[Producto, int]]) -> dict:
        items_confirmados = []
        errores = []
        total_general = 0

        # PROCESO 1: Transformación y validación de cada ítem
        for producto, cantidad in items_solicitados:
            if cantidad <= 0:
                errores.append(f"Cantidad inválida ({cantidad}) para {producto.nombre}")
                continue
            if producto.stock < cantidad:
                errores.append(
                    f"Sin stock suficiente para {producto.nombre} (Disponible: {producto.stock})"
                )
                continue
            if producto.precio <= 0:
                errores.append(f"Precio inválido para {producto.nombre}")
                continue

            # PROCESO 2: Actualización de estado (Descuento de stock) y cálculo de totales
            producto.stock -= cantidad
            subtotal = producto.precio * cantidad
            total_general += subtotal
            items_confirmados.append((producto, cantidad, subtotal))

        # ESTRUCTURACIÓN DE LAS SALIDAS
        return {
            "cliente": cliente.nombre,
            "codigo": cliente.codigo,
            "correo": cliente.correo,
            "items_confirmados": [
                f"{p.nombre} x{cant} - S/ {sub:.2f}"
                for p, cant, sub in items_confirmados
            ],
            "pedidos_cocina": [(p.nombre, cant) for p, cant, _ in items_confirmados],
            "total": total_general,
            "observaciones": errores,
        }


# ==========================================
# 1. ENTRADAS (INPUTS)
# ==========================================
# Base de datos inicial / Catálogo de productos disponibles
menu_productos = {
    "P001": Producto("P001", "Pieza de Pollo Broaster", precio=8.5, stock=10),
    "P002": Producto("P002", "Combo 2 Piezas + Papas", precio=18.0, stock=5),
    "P003": Producto("P003", "Papas Fritas", precio=6.0, stock=15),
    "P004": Producto("P004", "Gaseosa 500ml", precio=4.0, stock=20),
}

print("=== BROASTER GO - Nuevo Pedido ===")

# ENTRADA 1: Datos del cliente desde el teclado
codigo_cliente = input("Código del cliente: ").strip()
nombre_cliente = input("Nombre del cliente: ").strip()
correo_cliente = input("Correo del cliente: ").strip()

cliente1 = Cliente(
    codigo=codigo_cliente,
    nombre=nombre_cliente,
    correo=correo_cliente,
)

print("\n--- Menú disponible ---")
for p in menu_productos.values():
    print(f"{p.codigo} - {p.nombre} - S/ {p.precio:.2f} - Stock: {p.stock}")

# ENTRADA 2: Selección de productos y cantidades por teclado
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

# ==========================================
# 2. EJECUCIÓN DEL PROCESO
# ==========================================
# Se envían las ENTRADAS (cliente1, solicitud_pedido) al PROCESO
resultado = SistemaPedidos.procesar_pedido(cliente1, solicitud_pedido)

# ==========================================
# 3. SALIDAS (OUTPUTS)
# ==========================================
# SALIDA 1: Emisión de la boleta de venta
print("\n==========================================")
print("=== BOLETA - BROASTER GO ===")
print("==========================================")
print(f"Cliente: {resultado['cliente']} ({resultado['codigo']})")

print("\n Productos Confirmados:")
if resultado['items_confirmados']:
    for item in resultado['items_confirmados']:
        print(f" - {item}")
else:
    print(" (No se procesó ningún producto en esta orden)")

print(f"\n Total a pagar: S/ {resultado['total']:.2f}")

# SALIDA 2: Notificación al cliente
print("\n Notificación de confirmación:")
print(f" Enviado a: {resultado['correo']}")

# SALIDA 3: Comanda para la cocina
print("\n Pedido enviado al Panel de Cocina:")
for nombre, cantidad in resultado['pedidos_cocina']:
    print(f" - {cantidad} x {nombre}")

# SALIDA 4: Reporte de incidencias/errores
if resultado['observaciones']:
    print("\n Observaciones/Errores durante el proceso:")
    for err in resultado['observaciones']:
        print(f" - {err}")
