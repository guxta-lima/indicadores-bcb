import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import coletar


class TestColetar(unittest.TestCase):
    def test_converter_data(self):
        self.assertEqual(coletar.converter_data("09/10/2026"), "2026-10-09")

    def test_mesclar_nao_duplica_e_ordena(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "x.csv"
            coletar.mesclar(arq, [("2026-10-09", "5.0"), ("2026-10-08", "4.9")])
            linhas = coletar.mesclar(arq, [("2026-10-09", "9.9"), ("2026-10-10", "5.1")])
            self.assertEqual(
                linhas, [("2026-10-08", "4.9"), ("2026-10-09", "5.0"), ("2026-10-10", "5.1")]
            )

    def test_readme_marca_indisponivel(self):
        txt = coletar.gerar_readme({"dolar": ("2026-10-09", "4.98")}, datetime(2026, 10, 13, 21, 0))
        self.assertIn("| Dólar PTAX (venda) | 4.98 R$ | 2026-10-09 |", txt)
        self.assertIn("| Selic meta | indisponível | — |", txt)


if __name__ == "__main__":
    unittest.main()
