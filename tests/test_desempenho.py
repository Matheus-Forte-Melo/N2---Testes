import time
import pytest  # type: ignore[import]
from carrinho import Carrinho, CarrinhoService

@pytest.mark.slow
def test_calculo_resumo_eh_rapido(service: CarrinhoService, carrinho: Carrinho, produto_padrao) -> None:
    for _ in range(3):
        service.adicionar_item(carrinho, produto_padrao, 1)

    inicio = time.perf_counter()
    resumo = service.calcular_resumo(carrinho, "88000-000")
    duracao = time.perf_counter() - inicio

    assert duracao < 0.2
    assert resumo.total > 0
