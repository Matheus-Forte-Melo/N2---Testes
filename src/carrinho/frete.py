from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Protocol

from .exceptions import FreteIndisponivelError

CENT = Decimal("0.01")

@dataclass(frozen=True, slots=True)
class Frete:
    valor: Decimal
    prazo_dias: int

    def __post_init__(self) -> None:
        if self.valor < 0:
            raise ValueError("Valor do frete não pode ser negativo")
        if self.prazo_dias <= 0:
            raise ValueError("Prazo deve ser positivo")


class FreteAPI(Protocol):
    def cotacao(self, cep_origem: str, cep_destino: str, peso_total: float) -> Frete:
        ...


class TabelaFreteLocal:
    """Implementação determinística usada em testes de integração."""

    def __init__(self, *, prazo_base: int = 3) -> None:
        self._prazo_base = prazo_base

    def cotacao(self, cep_origem: str, cep_destino: str, peso_total: float) -> Frete:
        if peso_total <= 0:
            raise FreteIndisponivelError(cep_destino)
        faixa = self._selecionar_faixa(peso_total)
        valor = (Decimal("12.50") + Decimal(faixa) * Decimal("4.80")).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        prazo = self._prazo_base + int(max(1, peso_total // 5))
        return Frete(valor=valor, prazo_dias=prazo)

    @staticmethod
    def _selecionar_faixa(peso: float) -> int:
        if peso <= 3:
            return 1
        if peso <= 10:
            return 2
        if peso <= 20:
            return 3
        return 4
