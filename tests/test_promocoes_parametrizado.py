from decimal import Decimal
import pytest  # type: ignore[import]
from carrinho import Carrinho
from carrinho.services import CarrinhoService


@pytest.mark.parametrize(
    "quantidade, desconto_esperado",
    [
        (1, Decimal("0.00")),
        (2, Decimal("0.00")),
        (3, Decimal("780.00")),
        (5, Decimal("2600.00")),
        (9, Decimal("4680.00")),
        (10, Decimal("7800.00")),
        (12, Decimal("9360.00")),
    ],
)
def test_promocao_progressiva_por_quantidade(
    service: CarrinhoService, carrinho: Carrinho, produto_padrao, quantidade: int, desconto_esperado: Decimal
) -> None:
    service.adicionar_item(carrinho, produto_padrao, quantidade)
    resumo = service.calcular_resumo(carrinho, "88000-000")

    assert resumo.desconto_promocional == desconto_esperado
