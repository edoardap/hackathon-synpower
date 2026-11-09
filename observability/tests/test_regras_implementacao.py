import re
import unittest
from pathlib import Path

AVALIADORES = Path(__file__).parents[1] / "evaluators"
CODIGO, PEDIDO = "{{metadata.artifact.code}}", "{{input.value}}"
VARIAVEIS = {
    "task_completion": {"{{trace}}"},
    "scope_adherence": {"{{trace}}"},
    "test_adequacy": {"{{trace}}"},
    "rules_adherence": {CODIGO},
    "minimal_solution": {PEDIDO, CODIGO},
    "security": {CODIGO},
}


class RegrasDeImplementacaoTest(unittest.TestCase):
    def setUp(self):
        self.guia = (AVALIADORES / "configurar_regras_no_opik.md").read_text(encoding="utf-8")

    def test_cada_prompt_usa_so_as_variaveis_previstas_e_define_pass_e_fail(self):
        for nome, esperadas in VARIAVEIS.items():
            texto = (AVALIADORES / f"{nome}.md").read_text(encoding="utf-8")
            self.assertEqual(set(re.findall(r"\{\{[^}]+\}\}", texto)), esperadas, nome)
            self.assertIn("PASS:", texto, nome)
            self.assertIn("FAIL:", texto, nome)

    def test_guia_mapeia_cada_regra_e_cada_variavel_dela(self):
        for nome, esperadas in VARIAVEIS.items():
            self.assertIn(f"{nome}.md", self.guia, nome)
            for variavel in esperadas:
                self.assertIn(variavel, self.guia, f"{nome} {variavel}")

    def test_prompt_que_exige_regras_do_repositorio_deixa_o_marcador_para_colar(self):
        texto = (AVALIADORES / "rules_adherence.md").read_text(encoding="utf-8")
        self.assertIn("COLE AQUI", texto)


if __name__ == "__main__":
    unittest.main()
