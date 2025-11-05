from datetime import date, timedelta
from decimal import Decimal
import pytest  # type: ignore[import]
from carrinho import Carrinho, CarrinhoService, Cupom
from carrinho.entities import CarrinhoItem
from carrinho.exceptions import CupomExpiradoError, CupomInvalidoError

def test_cupom_expirado_gatilha_excecao(service: CarrinhoService, carrinho: Carrinho, produto_padrao) -> None:
    cupom = Cupom(codigo="PROMOFAIL", percentual=10, expira_em=date(2024, 12, 31))
    service.adicionar_item(carrinho, produto_padrao, 1)

    with pytest.raises(CupomExpiradoError):
        service.aplicar_cupom(carrinho, cupom)


def test_cupom_percentual_invalido() -> None:
    cupom = Cupom(codigo="BUG1000", percentual=150, expira_em=date.today() + timedelta(days=10))

    with pytest.raises(CupomInvalidoError):
        cupom.calcular_desconto(Decimal("100"), date.today())


def test_calculo_resumo_rejeita_carrinho_vazio(service: CarrinhoService, carrinho: Carrinho) -> None:
    with pytest.raises(ValueError):
        service.calcular_resumo(carrinho, "88000-000")


def test_alterar_quantidade_para_zero_falha(produto_padrao, carrinho: Carrinho) -> None:
    item = CarrinhoItem(produto_padrao, 1)
    carrinho.itens[produto_padrao.sku] = item

    with pytest.raises(ValueError):
        carrinho.alterar_quantidade(produto_padrao.sku, 0)
