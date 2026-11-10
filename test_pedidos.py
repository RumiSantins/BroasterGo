# Pruebas automáticas de broaster_go_pedidos.py (reglas R1 a R8 del README)
# Ejecutar con:  python -m unittest -v

import unittest

from broaster_go_pedidos import (
    Cliente,
    Producto,
    SistemaPedidos,
    calcular_cierre_caja,
    validar_cliente,
    validar_correo,
)


def cliente_de_prueba():
    return Cliente("N001", "Ana", "ana@gmail.com")


class PruebasValidacionCliente(unittest.TestCase):

    def test_correos_validos(self):
        self.assertTrue(validar_correo("ana@gmail.com"))
        self.assertTrue(validar_correo("jose.perez@upn.edu.pe"))

    def test_correos_invalidos(self):
        self.assertFalse(validar_correo(""))
        self.assertFalse(validar_correo("ana.gmail.com"))      # sin @
        self.assertFalse(validar_correo("ana@gmail"))          # sin punto en el dominio
        self.assertFalse(validar_correo("@gmail.com"))         # sin usuario
        self.assertFalse(validar_correo("ana@@gmail.com"))     # dos @
        self.assertFalse(validar_correo("ana @gmail.com"))     # con espacio

    def test_cliente_correcto_no_tiene_problemas(self):
        self.assertEqual(validar_cliente(cliente_de_prueba()), [])

    def test_cliente_sin_datos_tiene_tres_problemas(self):
        self.assertEqual(len(validar_cliente(Cliente("", "", ""))), 3)


class PruebasProcesarPedido(unittest.TestCase):

    def setUp(self):
        # se ejecuta antes de CADA prueba: productos nuevos con stock completo
        self.pollo = Producto("P001", "Pieza de Pollo Broaster", 8.5, 10)
        self.combo = Producto("P002", "Combo 2 Piezas + Papas", 18.0, 5)
        self.gaseosa = Producto("P004", "Gaseosa 500ml", 4.0, 20)

    def test_pedido_simple_calcula_total_y_descuenta_stock(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.pollo, 1), (self.gaseosa, 1)]
        )
        self.assertEqual(resultado["estado"], "Confirmado")
        self.assertEqual(resultado["total"], 12.5)
        self.assertEqual(self.pollo.stock, 9)
        self.assertEqual(self.gaseosa.stock, 19)

    def test_r1_cantidad_cero_o_negativa_no_se_acepta(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.pollo, 0), (self.gaseosa, -2), (self.combo, 1)]
        )
        self.assertEqual(len(resultado["items_confirmados"]), 1)
        self.assertEqual(len(resultado["observaciones"]), 2)
        self.assertEqual(self.pollo.stock, 10)

    def test_r2_precio_invalido_no_se_acepta(self):
        gratis = Producto("P999", "Producto mal cargado", 0, 10)
        resultado = SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(gratis, 1)])
        self.assertEqual(resultado["estado"], "Rechazado")
        self.assertEqual(gratis.stock, 10)

    def test_r3_sin_stock_suficiente(self):
        resultado = SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(self.combo, 6)])
        self.assertEqual(resultado["estado"], "Rechazado")
        self.assertIn("Sin stock suficiente", resultado["observaciones"][0])
        self.assertEqual(self.combo.stock, 5)

    def test_r3_mismo_producto_dos_veces_respeta_el_stock(self):
        # stock 5: el primer pedido de 4 entra, el segundo de 4 ya no
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 4), (self.combo, 4)]
        )
        self.assertEqual(len(resultado["items_confirmados"]), 1)
        self.assertEqual(self.combo.stock, 1)

    def test_r4_delivery_debajo_del_minimo_se_rechaza_y_devuelve_stock(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.pollo, 2)], zona="A"   # 17.00 < 25.00
        )
        self.assertEqual(resultado["estado"], "Rechazado")
        self.assertEqual(resultado["total"], 0)
        self.assertEqual(self.pollo.stock, 10)  # el stock vuelve a como estaba

    def test_r5_delivery_suma_la_tarifa_de_la_zona(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 2)], zona="c"   # 36.00 + 8.00
        )
        self.assertEqual(resultado["delivery"], 8.0)
        self.assertEqual(resultado["total"], 44.0)

    def test_r5_zona_sin_cobertura(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 2)], zona="Z"
        )
        self.assertEqual(resultado["estado"], "Rechazado")
        self.assertEqual(self.combo.stock, 5)

    def test_r6_cupon_valido_aplica_descuento(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 2)], cupon="broaster10"
        )
        self.assertEqual(resultado["descuento"], 3.6)   # 10% de 36.00
        self.assertEqual(resultado["total"], 32.4)

    def test_r6_cupon_inexistente_no_descuenta(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 2)], cupon="GRATIS100"
        )
        self.assertEqual(resultado["descuento"], 0)
        self.assertEqual(resultado["total"], 36.0)
        self.assertEqual(len(resultado["observaciones"]), 1)

    def test_r6_descuento_y_delivery_juntos(self):
        # 36.00 - 15% (5.40) + zona B (5.00) = 35.60
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 2)], zona="B", cupon="FAMILIA15"
        )
        self.assertEqual(resultado["total"], 35.6)

    def test_r7_forma_de_pago_no_aceptada(self):
        resultado = SistemaPedidos.procesar_pedido(
            cliente_de_prueba(), [(self.combo, 1)], forma_pago="Bitcoin"
        )
        self.assertEqual(resultado["estado"], "Rechazado")
        self.assertEqual(self.combo.stock, 5)

    def test_r8_alerta_cuando_el_stock_queda_en_3_o_menos(self):
        resultado = SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(self.combo, 2)])
        self.assertEqual(resultado["alertas_stock"], ["Combo 2 Piezas + Papas: solo quedan 3"])

    def test_r8_sin_alerta_si_hay_stock_de_sobra(self):
        resultado = SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(self.gaseosa, 1)])
        self.assertEqual(resultado["alertas_stock"], [])


class PruebasCierreCaja(unittest.TestCase):

    def test_cierre_suma_solo_los_pedidos_confirmados(self):
        pollo = Producto("P001", "Pieza de Pollo Broaster", 8.5, 10)
        pedidos = [
            SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(pollo, 2)], forma_pago="Yape"),
            SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(pollo, 1)], forma_pago="Efectivo"),
            SistemaPedidos.procesar_pedido(cliente_de_prueba(), [(pollo, 99)]),  # rechazado
        ]
        cierre = calcular_cierre_caja(pedidos)
        self.assertEqual(cierre["confirmados"], 2)
        self.assertEqual(cierre["rechazados"], 1)
        self.assertEqual(cierre["total_vendido"], 25.5)
        self.assertEqual(cierre["por_forma_pago"]["Yape"], 17.0)
        self.assertEqual(cierre["por_forma_pago"]["Efectivo"], 8.5)


if __name__ == "__main__":
    unittest.main()
