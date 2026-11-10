# Broaster GO - version con ventana (tkinter, ya viene con Python)
# Misma logica que broaster_go.py, pero pidiendo los datos con campos y botones.

import tkinter as tk
from tkinter import ttk, messagebox

from calculos import CARTA, IGV, calcular_totales, soles

# la ventana elige los articulos por nombre: nombre -> precio
PRECIOS = {}
for nombre_articulo, precio_articulo in CARTA.values():
    PRECIOS[nombre_articulo] = precio_articulo


class VentanaPedido:
    """Ventana del mostrador: arma el pedido, lo muestra y calcula el total."""

    def __init__(self, ventana):
        self.ventana = ventana
        self.pedido = []  # lista de (nombre, cantidad, importe)
        ventana.title("Broaster GO")

        tk.Label(ventana, text="Articulo:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.combo_articulo = ttk.Combobox(ventana, values=list(PRECIOS), state="readonly", width=20)
        self.combo_articulo.grid(row=0, column=1, padx=8, pady=4)

        tk.Label(ventana, text="Cantidad:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.entrada_cantidad = tk.Entry(ventana, width=22)
        self.entrada_cantidad.grid(row=1, column=1, padx=8, pady=4)
        self.entrada_cantidad.insert(0, "1")
        # presionar Enter en la cantidad hace lo mismo que el boton "Agregar"
        self.entrada_cantidad.bind("<Return>", self.agregar)

        tk.Button(ventana, text="Agregar", command=self.agregar).grid(row=2, column=1, sticky="e", padx=8, pady=4)

        self.lista_pedido = tk.Listbox(ventana, width=40, height=8)
        self.lista_pedido.grid(row=3, column=0, columnspan=2, padx=8, pady=4)

        tk.Button(ventana, text="Quitar seleccionado", command=self.quitar).grid(row=4, column=0, sticky="w", padx=8, pady=4)
        self.etiqueta_subtotal = tk.Label(ventana, text="Subtotal: " + soles(0), font=("Arial", 10, "bold"))
        self.etiqueta_subtotal.grid(row=4, column=1, sticky="e", padx=8, pady=4)

        tk.Label(ventana, text="Descuento (%):").grid(row=5, column=0, sticky="w", padx=8, pady=4)
        self.entrada_descuento = tk.Entry(ventana, width=22)
        self.entrada_descuento.grid(row=5, column=1, padx=8, pady=4)

        tk.Button(ventana, text="Cancelar pedido", command=self.cancelar).grid(row=6, column=0, sticky="w", padx=8, pady=8)
        tk.Button(ventana, text="Finalizar pedido", command=self.finalizar).grid(row=6, column=1, sticky="e", padx=8, pady=8)

    # ---------- calculos ----------
    def calcular_subtotal(self):
        subtotal = 0.0
        for nombre, cantidad, importe in self.pedido:
            subtotal = subtotal + importe
        return subtotal

    def actualizar_subtotal(self):
        self.etiqueta_subtotal.config(text="Subtotal: " + soles(self.calcular_subtotal()))

    def leer_descuento(self):
        # campo vacio = sin cupon. Devuelve None si lo escrito no sirve.
        texto = self.entrada_descuento.get().strip()
        if texto == "":
            return 0.0
        try:
            porcentaje = float(texto)
        except ValueError:
            return None
        if porcentaje < 0 or porcentaje > 100:
            return None
        return porcentaje

    # ---------- botones ----------
    def agregar(self, evento=None):
        # "evento" lo envia tkinter cuando se presiona Enter; con el boton llega vacio
        nombre = self.combo_articulo.get()
        if nombre not in PRECIOS:
            messagebox.showerror("Broaster GO", "Seleccione un articulo.")
            return

        try:
            cantidad = int(self.entrada_cantidad.get())
        except ValueError:
            messagebox.showerror("Broaster GO", "La cantidad debe ser un numero entero.")
            return

        if cantidad <= 0:
            messagebox.showerror("Broaster GO", "La cantidad debe ser mayor que cero.")
            return

        importe = PRECIOS[nombre] * cantidad
        self.pedido.append((nombre, cantidad, importe))
        self.lista_pedido.insert(tk.END, str(cantidad) + " x " + nombre + " = " + soles(importe))
        self.actualizar_subtotal()

    def quitar(self):
        seleccion = self.lista_pedido.curselection()
        if len(seleccion) == 0:
            messagebox.showinfo("Broaster GO", "Seleccione en la lista el articulo que desea quitar.")
            return

        posicion = seleccion[0]
        self.lista_pedido.delete(posicion)
        del self.pedido[posicion]  # la lista y self.pedido tienen el mismo orden
        self.actualizar_subtotal()

    def finalizar(self):
        if len(self.pedido) == 0:
            messagebox.showinfo("Broaster GO", "El pedido esta vacio.")
            return

        porcentaje = self.leer_descuento()
        if porcentaje is None:
            messagebox.showerror("Broaster GO", "El descuento debe ser un numero entre 0 y 100.")
            return

        totales = calcular_totales(self.calcular_subtotal(), porcentaje)

        detalle = ""
        for nombre, cantidad, importe in self.pedido:
            detalle = detalle + str(cantidad) + " x " + nombre + "  " + soles(importe) + "\n"

        messagebox.showinfo(
            "Broaster GO",
            detalle + "\n"
            + "Subtotal:      " + soles(totales["subtotal"]) + "\n"
            + "Descuento:    -" + soles(totales["descuento"]) + "\n"
            + "IGV (" + format(IGV * 100, "g") + "%):     " + soles(totales["igv"]) + "\n"
            + "TOTAL A PAGAR: " + soles(totales["total"]) + "\n\n"
            + "Gracias por elegir Broaster GO!"
        )
        self.limpiar()  # la ventana queda lista para el siguiente cliente

    def cancelar(self):
        if len(self.pedido) == 0:
            return
        if messagebox.askyesno("Broaster GO", "Desea borrar el pedido actual?"):
            self.limpiar()

    def limpiar(self):
        self.pedido = []
        self.lista_pedido.delete(0, tk.END)
        self.combo_articulo.set("")
        self.entrada_cantidad.delete(0, tk.END)
        self.entrada_cantidad.insert(0, "1")
        self.entrada_descuento.delete(0, tk.END)
        self.actualizar_subtotal()


def main():
    ventana = tk.Tk()
    VentanaPedido(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()
