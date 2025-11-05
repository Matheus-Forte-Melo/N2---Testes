from datetime import date, timedelta
from decimal import Decimal
from typing import Callable, Iterator
from unittest.mock import Mock
import pytest  # type: ignore[import]
from carrinho import Carrinho, CarrinhoService, Cupom, Produto
from carrinho.frete import Frete, FreteAPI
from carrinho.repositories import InMemoryEstoqueRepository


@pytest.fixture
def estoque() -> Iterator[InMemoryEstoqueRepository]:
    repo = InMemoryEstoqueRepository()
    repo.registrar("SKU-001", 25)
    repo.registrar("SKU-002", 10)
    yield repo
    # teardown explícito para demonstrar controle do ciclo de vida
    repo.snapshot()

@pytest.fixture
def frete_api() -> Mock:
    api = Mock(spec=FreteAPI)
    api.cotacao.return_value = Frete(valor=Decimal("27.30"), prazo_dias=4)
    return api

@pytest.fixture
def data_congelada() -> Callable[[], date]:
    base = date(2025, 1, 15)
    return lambda: base

@pytest.fixture
def service(estoque: InMemoryEstoqueRepository, frete_api: Mock, data_congelada: Callable[[], date]) -> CarrinhoService:
    return CarrinhoService(estoque, frete_api, data_provider=data_congelada)

@pytest.fixture
def carrinho() -> Carrinho:
    return Carrinho()

@pytest.fixture
def produto_padrao() -> Produto:
    return Produto(sku="SKU-001", nome="Notebook Gamer", preco=Decimal("5200.00"), peso_kg=2.8)

@pytest.fixture
def cupom_valido(data_congelada: Callable[[], date]) -> Cupom:
    return Cupom(codigo="PROMO10", percentual=10, expira_em=data_congelada() + timedelta(days=30))
