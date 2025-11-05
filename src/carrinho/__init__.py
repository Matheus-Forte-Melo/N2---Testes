# Critérios: Integração simulada (API pública clara), Design de testes
from .entities import Carrinho, CarrinhoItem, Cupom, Produto
from .exceptions import (
    CupomExpiradoError,
    CupomInvalidoError,
    EstoqueInsuficienteError,
    FreteIndisponivelError,
    ItemInexistenteError,
)
from .frete import Frete, FreteAPI
from .repositories import EstoqueRepository, InMemoryEstoqueRepository
from .services import CarrinhoService

__all__ = [
    "Carrinho",
    "CarrinhoItem",
    "CarrinhoService",
    "Cupom",
    "CupomExpiradoError",
    "CupomInvalidoError",
    "EstoqueInsuficienteError",
    "Frete",
    "FreteAPI",
    "FreteIndisponivelError",
    "InMemoryEstoqueRepository",
    "ItemInexistenteError",
    "Produto",
    "EstoqueRepository",
]
