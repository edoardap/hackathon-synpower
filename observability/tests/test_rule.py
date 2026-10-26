import json
import re
import unittest
from pathlib import Path

AVALIADORES = Path(__file__).parents[1] / "evaluators"


class RegraCodeQualityTest(unittest.TestCase):
    def setUp(self):
        self.rubrica = (AVALIADORES / "code_quality.md").read_text(encoding="utf-8")
        self.regra = json.loads((AVALIADORES / "code_quality_rule.json").read_text(encoding="utf-8"))

    def test_variaveis_da_rubrica_sao_as_do_mapeamento(self):
        usadas = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", self.rubrica))
        self.assertEqual(usadas, set(self.regra["code"]["variables"]))

    def test_mapeamento_aponta_para_campos_do_trace(self):
        self.assertEqual(
            self.regra["code"]["variables"], {"pedido": "input.value", "codigo": "metadata.artifact.code"}
        )

    def test_mensagem_da_regra_e_a_rubrica(self):
        (mensagem,) = self.regra["code"]["messages"]
        self.assertEqual(mensagem["content"].strip(), self.rubrica.strip())

    def test_regra_amostra_tudo_e_filtra_pela_tag(self):
        self.assertEqual(self.regra["sampling_rate"], 1)
        self.assertIn(
            {"field": "tags", "operator": "contains", "value": "code_written"}, self.regra["filters"]
        )
        self.assertEqual(self.regra["code"]["schema"][0]["name"], self.regra["name"])


if __name__ == "__main__":
    unittest.main()
