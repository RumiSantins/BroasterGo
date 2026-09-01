# Broaster GO - version con ventana (tkinter, ya viene con Python)
# Misma logica que broaster_go.py, pero pidiendo los datos con campos y botones.

import tkinter as tk
from tkinter import ttk, messagebox

IGV = 0.18  # 18% en Peru

CARTA = {
    "Combo Zinger": 60.0,
    "Combo 3 piezas": 40.0,
    "Combo familiar": 90.0,
    "Bebida": 7.0,
    "Papas": 15.0,
}

pedido = []  # lista de (nombre, cantidad, importe)


def agregar():
    nombre = combo_articulo.get()
    if nombre not in CARTA:
        messagebox.showerror("Broaster GO", "Seleccione un articulo.")
        return

    try:
        cantidad = int(entrada_cantidad.get())
    except ValueError:
        messagebox.showerror("Broaster GO", "La cantidad debe ser un numero entero.")
        return

    if cantidad <= 0:
        messagebox.showerror("Broaster GO", "La cantidad debe ser mayor que cero.")
        return

    importe = CARTA[nombre] * cantidad
    pedido.append((nombre, cantidad, importe))
    lista_pedido.insert(tk.END, str(cantidad) + " x " + nombre + " = S/ " + format(importe, ".2f"))


def finalizar():
    if len(pedido) == 0:
        messagebox.showinfo("Broaster GO", "El pedido esta vacio.")
        return

    subtotal = 0.0
    for nombre, cantidad, importe in pedido:
        subtotal = subtotal + importe

    try:
        porcentaje = float(entrada_descuento.get())
    except ValueError:
        porcentaje = 0.0  # si el campo esta vacio o mal escrito, no hay cupon

    impuesto = subtotal * IGV
    monto_descuento = subtotal * (porcentaje / 100)
    total = subtotal + impuesto - monto_descuento

    messagebox.showinfo(
        "Broaster GO",
        "Subtotal:      S/ " + format(subtotal, ".2f") + "\n"
        + "IGV (18%):     S/ " + format(impuesto, ".2f") + "\n"
        + "Descuento:    -S/ " + format(monto_descuento, ".2f") + "\n"
        + "TOTAL A PAGAR: S/ " + format(total, ".2f") + "\n\n"
        + "Gracias por elegir Broaster GO!"
    )


# ---------- ventana ----------
ventana = tk.Tk()
ventana.title("Broaster GO")

tk.Label(ventana, text="Articulo:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
combo_articulo = ttk.Combobox(ventana, values=list(CARTA), state="readonly", width=20)
combo_articulo.grid(row=0, column=1, padx=8, pady=4)

tk.Label(ventana, text="Cantidad:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
entrada_cantidad = tk.Entry(ventana, width=22)
entrada_cantidad.grid(row=1, column=1, padx=8, pady=4)

tk.Button(ventana, text="Agregar", command=agregar).grid(row=2, column=1, sticky="e", padx=8, pady=4)

lista_pedido = tk.Listbox(ventana, width=40, height=8)
lista_pedido.grid(row=3, column=0, columnspan=2, padx=8, pady=4)

tk.Label(ventana, text="Descuento (%):").grid(row=4, column=0, sticky="w", padx=8, pady=4)
entrada_descuento = tk.Entry(ventana, width=22)
entrada_descuento.grid(row=4, column=1, padx=8, pady=4)

tk.Button(ventana, text="Finalizar pedido", command=finalizar).grid(row=5, column=1, sticky="e", padx=8, pady=8)

if __name__ == "__main__":
    ventana.mainloop()
