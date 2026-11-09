import unittest

from observability.evaluators import heuristics
from observability.tracing.turno import Span

NEGADO = "Acesso negado pela politica de segredos: casa com o padrao .pem"
PRECOS = {"m": {"input": 2.0, "output": 10.0}}


def chat(entrada, saida, modelo="m", lido=0, criado=0):
    """`entrada` é o total, com o cache dentro, como o adaptador grava."""
    return Span("chat", 1, 2, {
        "gen_ai.request.model": modelo, "gen_ai.usage.input_tokens": entrada, "gen_ai.usage.output_tokens": saida,
        "gen_ai.usage.cache_read.input_tokens": lido, "gen_ai.usage.cache_creation.input_tokens": criado,
    })


def turno(*filhos):
    return Span("turno", 0, 9, filhos=list(filhos))


class FalhasETagsTest(unittest.TestCase):
    def test_duas_ferramentas_e_uma_negada_pelo_guard(self):
        t = turno(Span("Bash", 1, 2, saida="ok"), Span("Read", 2, 3, saida=NEGADO))
        scores, tags = heuristics.calcular(t, PRECOS)
        self.assertEqual((scores["tool_failure_rate"], scores["guard_blocks"]), (0.5, 1))
        self.assertEqual(tags, ["tool_failure", "guard_block"])

    def test_bloqueio_do_claude_marcado_como_erro_conta_uma_vez(self):
        t = turno(Span("Read", 1, 2, saida=NEGADO, erro=True))
        scores, _ = heuristics.calcular(t, PRECOS)
        self.assertEqual((scores["tool_failure_rate"], scores["guard_blocks"]), (1.0, 1))

    def test_falha_comum_e_falha_sem_ser_bloqueio(self):
        t = turno(Span("exec", 1, 2, saida="Process exited with code 1", erro=True), Span("Read", 2, 3, saida="ok"))
        scores, tags = heuristics.calcular(t, PRECOS)
        self.assertEqual((scores["tool_failure_rate"], scores["guard_blocks"], tags), (0.5, 0, ["tool_failure"]))

    def test_ferramenta_de_subagente_entra_na_conta(self):
        t = turno(Span("Agent", 1, 5, saida="feito", filhos=[Span("Read", 2, 3, saida=NEGADO)]), Span("Bash", 6, 7, saida="ok"))
        scores, tags = heuristics.calcular(t, PRECOS)
        self.assertEqual((scores["tool_failure_rate"], scores["guard_blocks"], tags), (0.5, 1, ["tool_failure", "guard_block"]))

    def test_bloqueio_no_subagente_conta_uma_vez(self):
        t = turno(Span("Agent", 1, 5, saida=NEGADO, filhos=[Span("Read", 2, 3, saida=NEGADO)]))
        scores, _ = heuristics.calcular(t, PRECOS)
        self.assertEqual((scores["tool_failure_rate"], scores["guard_blocks"]), (1.0, 1))

    def test_turno_sem_ferramenta_nem_falha_nao_tem_tag(self):
        scores, tags = heuristics.calcular(turno(chat(1, 1)), PRECOS)
        self.assertEqual((scores["tool_failure_rate"], scores["guard_blocks"], tags), (0.0, 0, []))


class TokensECustoTest(unittest.TestCase):
    def test_tokens_somam_os_chats_inclusive_os_do_subagente(self):
        sub = Span("Agent", 2, 4, filhos=[chat(30, 5)])
        scores, _ = heuristics.calcular(turno(chat(10, 2), sub, chat(100, 20)), PRECOS)
        self.assertEqual(scores["tokens_total"], 167)

    def test_custo_pela_tabela_por_milhao_de_tokens(self):
        scores, _ = heuristics.calcular(turno(chat(1_000_000, 500_000)), PRECOS)
        self.assertEqual(scores["cost_usd"], 7.0)

    def test_cache_cobra_leitura_e_escrita_pelos_precos_proprios(self):
        precos = {"m": {"input": 2.0, "output": 10.0, "cache_read": 0.2, "cache_write": 2.5}}
        # 1 000 novos, 99 000 lidos do cache, 10 000 escritos no cache e 500 de saída
        scores, _ = heuristics.calcular(turno(chat(110_000, 500, lido=99_000, criado=10_000)), precos)
        self.assertEqual(scores["cost_usd"], 0.0518)
        self.assertEqual(scores["tokens_total"], 110_500)

    def test_sem_preco_de_cache_o_cache_custa_como_entrada(self):
        scores, _ = heuristics.calcular(turno(chat(110_000, 500, lido=99_000, criado=10_000)), PRECOS)
        self.assertEqual(scores["cost_usd"], 0.225)

    def test_custo_bate_com_o_que_o_opik_calculou_para_os_mesmos_tokens(self):
        # entrada total, saída, lido, criado e o custo do span no Opik, em 2026-10-23
        medidos = {
            "claude-sonnet-5-5": (178_913, 10_024, 177_091, 1_818, 0.1225021),
            "claude-opus-5-5": (84_093, 392, 83_644, 447, 0.0268118),
            "claude-haiku-5-5": (162_945, 9_136, 159_132, 3_811, 0.006635895),
        }
        for modelo, (entrada, saida, lido, criado, opik) in medidos.items():
            scores, _ = heuristics.calcular(turno(chat(entrada, saida, modelo, lido, criado)))
            self.assertEqual(scores["cost_usd"], round(opik, 6), modelo)

    def test_modelo_fora_da_tabela_mantem_tokens_e_omite_o_custo(self):
        scores, _ = heuristics.calcular(turno(chat(10, 2), chat(5, 1, modelo="desconhecido")), PRECOS)
        self.assertEqual(scores["tokens_total"], 18)
        self.assertNotIn("cost_usd", scores)

    def test_turno_sem_chat_omite_o_custo(self):
        scores, _ = heuristics.calcular(turno(Span("Bash", 1, 2, saida="ok")), PRECOS)
        self.assertNotIn("cost_usd", scores)

    def test_tabela_do_repositorio_cobre_os_modelos_claude(self):
        self.assertLessEqual({"claude-sonnet-5-5", "claude-opus-5-5", "claude-haiku-5-5"}, heuristics.carregar_precos().keys())


if __name__ == "__main__":
    unittest.main()
