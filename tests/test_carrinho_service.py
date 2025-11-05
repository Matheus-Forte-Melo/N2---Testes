from decimal import Decimal
import pytest # type: ignore[import]
from carrinho import Carrinho, CarrinhoService
from carrinho.exceptions import EstoqueInsuficienteError


def test_adicionar_item_reserva_estoque(service: CarrinhoService, carrinho: Carrinho, produto_padrao, estoque) -> None:
    service.adicionar_item(carrinho, produto_padrao, 2)
    assert carrinho.quantidade_total == 2
    assert estoque.quantidade_disponivel("SKU-001") == 23

def test_alterar_quantidade_libera_e_reserva(service: CarrinhoService, carrinho: Carrinho, produto_padrao, estoque) -> None:
    service.adicionar_item(carrinho, produto_padrao, 4)
    service.alterar_quantidade(carrinho, "SKU-001", 2)

    assert carrinho.quantidade_total == 2
    assert estoque.quantidade_disponivel("SKU-001") == 23

    service.alterar_quantidade(carrinho, "SKU-001", 5)
    assert carrinho.quantidade_total == 5
    assert estoque.quantidade_disponivel("SKU-001") == 20

def test_remover_item_libera_reserva(service: CarrinhoService, carrinho: Carrinho, produto_padrao, estoque) -> None:
    service.adicionar_item(carrinho, produto_padrao, 3)
    service.remover_item(carrinho, "SKU-001")

    assert carrinho.quantidade_total == 0
    assert estoque.quantidade_disponivel("SKU-001") == 25

def test_nao_reserva_estoque_insuficiente(service: CarrinhoService, carrinho: Carrinho, produto_padrao) -> None:
    with pytest.raises(EstoqueInsuficienteError):
        service.adicionar_item(carrinho, produto_padrao, 30)

def test_calcula_resumo_com_cupom_e_promocao(service: CarrinhoService, carrinho: Carrinho, produto_padrao, cupom_valido, frete_api) -> None:
    service.adicionar_item(carrinho, produto_padrao, 3)
    service.aplicar_cupom(carrinho, cupom_valido)

    resumo = service.calcular_resumo(carrinho, "88000-000")

    assert resumo.valor_bruto == Decimal("15600.00")
    assert resumo.desconto_promocional == Decimal("780.00")
    assert resumo.desconto_cupom == Decimal("1482.00")
    assert resumo.total == Decimal("13365.30")
    frete_api.cotacao.assert_called_once()