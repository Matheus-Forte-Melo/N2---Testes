from dataclasses import dataclass
from typing import Dict, Protocol, runtime_checkable

from .exceptions import EstoqueInsuficienteError


@runtime_checkable
class EstoqueRepository(Protocol):
    def registrar(self, sku: str, quantidade: int) -> None:
        ...

    def reservar(self, sku: str, quantidade: int) -> None:
        ...

    def liberar(self, sku: str, quantidade: int) -> None:
        ...

    def confirmar_reserva(self, sku: str, quantidade: int) -> None:
        ...

    def quantidade_disponivel(self, sku: str) -> int:
        ...

@dataclass
class _EstoqueItem:
    disponivel: int
    reservado: int = 0

class InMemoryEstoqueRepository:
    """Repositório de estoque com reservas atômicas para uso em testes."""

    def __init__(self) -> None:
        self._itens: Dict[str, _EstoqueItem] = {}

    def registrar(self, sku: str, quantidade: int) -> None:
        if quantidade < 0:
            raise ValueError("Quantidade de registro deve ser não-negativa")
        self._itens[sku] = _EstoqueItem(disponivel=quantidade)

    def reservar(self, sku: str, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        item = self._itens.get(sku)
        if item is None:
            raise EstoqueInsuficienteError(sku, quantidade, 0)
        if item.disponivel < quantidade:
            raise EstoqueInsuficienteError(sku, quantidade, item.disponivel)
        item.disponivel -= quantidade
        item.reservado += quantidade

    def liberar(self, sku: str, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        item = self._itens.get(sku)
        if item is None or item.reservado < quantidade:
            raise EstoqueInsuficienteError(sku, quantidade, 0)
        item.disponivel += quantidade
        item.reservado -= quantidade

    def confirmar_reserva(self, sku: str, quantidade: int) -> None:
        item = self._itens.get(sku)
        if item is None or item.reservado < quantidade:
            raise EstoqueInsuficienteError(sku, quantidade, 0)
        item.reservado -= quantidade

    def quantidade_disponivel(self, sku: str) -> int:
        item = self._itens.get(sku)
        if item is None:
            return 0
        return item.disponivel

    # Auxiliar usado em testes de integração para inspecionar o estado.
    def snapshot(self) -> Dict[str, Dict[str, int]]:
        return {
            sku: {"disponivel": dados.disponivel, "reservado": dados.reservado}
            for sku, dados in self._itens.items()
        }
