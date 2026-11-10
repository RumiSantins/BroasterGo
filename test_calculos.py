# Pruebas automaticas de calculos.py
# Ejecutar con:  python -m unittest -v

import unittest

from calculos import calcular_totales, limitar_porcentaje, soles


class PruebasCalculos(unittest.TestCase):

    def test_sin_descuento_suma_el_igv(self):
        totales = calcular_totales(100.0, 0)
        self.assertEqual(totales["descuento"], 0.0)
        self.assertEqual(totales["igv"], 18.0)
        self.assertEqual(totales["total"], 118.0)

    def test_el_descuento_se_resta_antes_del_igv(self):
        # 100 - 10% = 90 ; IGV de 90 = 16.20 ; total = 106.20
        # (la version anterior daba 108.00 porque cobraba IGV sobre el descuento)
        totales = calcular_totales(100.0, 10)
        self.assertEqual(totales["descuento"], 10.0)
        self.assertEqual(totales["igv"], 16.2)
        self.assertEqual(totales["total"], 106.2)

    def test_descuento_del_100_por_ciento_deja_total_cero(self):
        self.assertEqual(calcular_totales(60.0, 100)["total"], 0.0)

    def test_porcentajes_fuera_de_rango_se_corrigen(self):
        self.assertEqual(limitar_porcentaje(-5), 0.0)
        self.assertEqual(limitar_porcentaje(150), 100.0)
        self.assertEqual(limitar_porcentaje(15), 15)
        # un descuento mayor al 100% ya no puede dejar el total en negativo
        self.assertGreaterEqual(calcular_totales(50.0, 300)["total"], 0)

    def test_formato_en_soles(self):
        self.assertEqual(soles(12.5), "S/ 12.50")
        self.assertEqual(soles(0), "S/ 0.00")


if __name__ == "__main__":
    unittest.main()
