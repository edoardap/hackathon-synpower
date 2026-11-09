import unittest

from observability.adapters import hook


class EstruturaTest(unittest.TestCase):
    def test_forma_nao_vaza_valores_e_preserva_ligacao_de_ids(self):
        f = hook.forma({"id": "abc", "tool_use_id": "abc", "name": "Bash", "texto": "segredo-123", "n": 3})
        self.assertEqual(f["id"], f["tool_use_id"])
        self.assertNotEqual(f["id"], "abc")
        self.assertEqual((f["name"], f["n"], f["texto"]), ("Bash", 3, "<str 11>"))

    def test_forma_marca_bloqueio_do_guard(self):
        self.assertEqual(hook.forma({"c": "Acesso negado pela politica de segredos"})["c"], "<str 39 guard>")


if __name__ == "__main__":
    unittest.main()
