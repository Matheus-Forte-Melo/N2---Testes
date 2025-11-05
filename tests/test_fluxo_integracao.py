import json
from datetime import date, timedelta
from decimal import Decimal
from carrinho import Carrinho, CarrinhoService, Cupom, Produto
from carrinho.frete import TabelaFreteLocal
from carrinho.repositories import InMemoryEstoqueRepository

def test_fluxo_completo_salva_resumo(tmp_path) -> None:
    estoque = InMemoryEstoqueRepository()
    estoque.registrar("SKU-001", 10)
    estoque.registrar("SKU-002", 8)

    frete = TabelaFreteLocal(prazo_base=2)
    service = CarrinhoService(estoque, frete, data_provider=lambda: date(2025, 1, 15))
    carrinho = Carrinho()

    produto1 = Produto(sku="SKU-001", nome="Mouse Premium", preco=Decimal("250.00"), peso_kg=0.3)
    produto2 = Produto(sku="SKU-002", nome="Teclado Mecânico", preco=Decimal("650.00"), peso_kg=1.1)

    service.adicionar_item(carrinho, produto1, 3)
    service.adicionar_item(carrinho, produto2, 2)

    cupom = Cupom(codigo="EQUIPE15", percentual=15, expira_em=date(2025, 2, 15))
    service.aplicar_cupom(carrinho, cupom)

    resumo = service.finalizar(carrinho, "88000-000")

    assert carrinho.esta_vazio()
    snapshot = estoque.snapshot()
    assert snapshot["SKU-001"] == {"disponivel": 7, "reservado": 0}
    assert snapshot["SKU-002"] == {"disponivel": 6, "reservado": 0}

    arquivo_resumo = tmp_path / "resumo.json"
    arquivo_resumo.write_text(
        json.dumps(
            {
                "valor_bruto": str(resumo.valor_bruto),
                "desconto_promocional": str(resumo.desconto_promocional),
                "desconto_cupom": str(resumo.desconto_cupom),
                "frete": str(resumo.frete.valor),
                "total": str(resumo.total),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    carregado = json.loads(arquivo_resumo.read_text(encoding="utf-8"))
    assert carregado["total"] == str(resumo.total)
