from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
from .exceptions import CupomExpiradoError, CupomInvalidoError, ItemInexistenteError

CENT = Decimal("0.01")

def _quantizar(valor: Decimal) -> Decimal:
    """Arredonda valores monetários para 2 casas utilizando half-up."""
    return valor.quantize(CENT, rounding=ROUND_HALF_UP)

@dataclass(frozen=True, slots=True)
class Produto:
    sku: str
    nome: str
    preco: Decimal
    peso_kg: float
    categoria: str = "geral"
    ativo: bool = True

    def __post_init__(self) -> None:
        if not self.sku:
            raise ValueError("SKU não pode ser vazio")
        if self.preco <= 0:
            raise ValueError("Preço deve ser positivo")
        if self.peso_kg <= 0:
            raise ValueError("Peso deve ser positivo")
        object.__setattr__(self, "preco", _quantizar(Decimal(self.preco)))


@dataclass(slots=True)
class CarrinhoItem:
    produto: Produto
    quantidade: int

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")

    def aumentar(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade para aumentar deve ser positiva")
        self.quantidade += quantidade

    def reduzir_para(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        self.quantidade = quantidade

    @property
    def subtotal(self) -> Decimal:
        return _quantizar(self.produto.preco * self.quantidade)


@dataclass(frozen=True, slots=True)
class Cupom:
    codigo: str
    percentual: int
    expira_em: date

    def calcular_desconto(self, valor: Decimal, referencia: date) -> Decimal:
        if not 0 < self.percentual <= 100:
            raise CupomInvalidoError(f"Percentual inválido para cupom {self.codigo!r}")
        if referencia > self.expira_em:
            raise CupomExpiradoError(self.codigo, self.expira_em, referencia)
        return _quantizar(valor * Decimal(self.percentual) / Decimal(100))


@dataclass(slots=True)
class Carrinho:
    itens: Dict[str, CarrinhoItem] = field(default_factory=dict)
    cupom: Optional[Cupom] = None

    def adicionar(self, produto: Produto, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        existente = self.itens.get(produto.sku)
        if existente:
            existente.aumentar(quantidade)
        else:
            self.itens[produto.sku] = CarrinhoItem(produto=produto, quantidade=quantidade)

    def alterar_quantidade(self, sku: str, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        item = self.itens.get(sku)
        if item is None:
            raise ItemInexistenteError(sku)
        item.reduzir_para(quantidade)

    def remover(self, sku: str) -> None:
        if sku not in self.itens:
            raise ItemInexistenteError(sku)
        self.itens.pop(sku)

    def registrar_cupom(self, cupom: Cupom) -> None:
        self.cupom = cupom

    @property
    def quantidade_total(self) -> int:
        return sum(item.quantidade for item in self.itens.values())

    @property
    def valor_bruto(self) -> Decimal:
        total = sum(item.subtotal for item in self.itens.values())
        return _quantizar(total)

    @property
    def peso_total(self) -> float:
        return sum(item.produto.peso_kg * item.quantidade for item in self.itens.values())

    def esta_vazio(self) -> bool:
        return not self.itens

    def limpar(self) -> None:
        self.itens.clear()
        self.cupom = None
