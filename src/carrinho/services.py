from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable

from .entities import Carrinho, Cupom, Produto
from .exceptions import FreteIndisponivelError
from .frete import Frete, FreteAPI
from .repositories import EstoqueRepository

CENT = Decimal("0.01")
CEP_ORIGEM_PADRAO = "01000-000"


@dataclass(frozen=True, slots=True)
class ResumoPedido:
    valor_bruto: Decimal
    desconto_promocional: Decimal
    desconto_cupom: Decimal
    frete: Frete
    total: Decimal

    def __post_init__(self) -> None:
        if self.total < 0:
            raise ValueError("Total não pode ser negativo")


class CarrinhoService:
    def __init__(
        self,
        estoque: EstoqueRepository,
        frete_api: FreteAPI,
        *,
        data_provider: Callable[[], date] | None = None,
        cep_origem: str = CEP_ORIGEM_PADRAO,
    ) -> None:
        self._estoque = estoque
        self._frete_api = frete_api
        self._hoje = data_provider or date.today
        self._cep_origem = cep_origem

    def adicionar_item(self, carrinho: Carrinho, produto: Produto, quantidade: int) -> None:
        self._estoque.reservar(produto.sku, quantidade)
        try:
            carrinho.adicionar(produto, quantidade)
        except Exception:
            self._estoque.liberar(produto.sku, quantidade)
            raise

    def alterar_quantidade(self, carrinho: Carrinho, sku: str, quantidade: int) -> None:
        item = carrinho.itens.get(sku)
        if item is None:
            raise ValueError(f"SKU {sku} não está no carrinho")
        delta = quantidade - item.quantidade
        if delta > 0:
            self._estoque.reservar(sku, delta)
        elif delta < 0:
            self._estoque.liberar(sku, -delta)
        carrinho.alterar_quantidade(sku, quantidade)

    def remover_item(self, carrinho: Carrinho, sku: str) -> None:
        item = carrinho.itens.get(sku)
        if item is None:
            raise ValueError(f"SKU {sku} não está no carrinho")
        self._estoque.liberar(sku, item.quantidade)
        carrinho.remover(sku)

    def aplicar_cupom(self, carrinho: Carrinho, cupom: Cupom) -> None:
        # Validamos utilizando um valor simbólico para garantir erros imediatos.
        cupom.calcular_desconto(Decimal("1.00"), self._hoje())
        carrinho.registrar_cupom(cupom)

    def calcular_resumo(self, carrinho: Carrinho, cep_destino: str) -> ResumoPedido:
        if carrinho.esta_vazio():
            raise ValueError("Carrinho não pode estar vazio ao calcular resumo")
        valor_bruto = carrinho.valor_bruto
        desconto_promocional = self._calcular_promocao(valor_bruto, carrinho.quantidade_total)
        base_para_cupom = valor_bruto - desconto_promocional
        desconto_cupom = (
            carrinho.cupom.calcular_desconto(base_para_cupom, self._hoje())
            if carrinho.cupom
            else Decimal("0.00")
        )
        frete = self._cotacao_frete(cep_destino, carrinho.peso_total)
        total = (valor_bruto - desconto_promocional - desconto_cupom + frete.valor).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        return ResumoPedido(
            valor_bruto=valor_bruto,
            desconto_promocional=desconto_promocional,
            desconto_cupom=desconto_cupom,
            frete=frete,
            total=total,
        )

    def finalizar(self, carrinho: Carrinho, cep_destino: str) -> ResumoPedido:
        resumo = self.calcular_resumo(carrinho, cep_destino)
        for item in carrinho.itens.values():
            self._estoque.confirmar_reserva(item.produto.sku, item.quantidade)
        carrinho.limpar()
        return resumo

    def _cotacao_frete(self, cep_destino: str, peso_total: float) -> Frete:
        frete = self._frete_api.cotacao(self._cep_origem, cep_destino, peso_total)
        if frete is None:
            raise FreteIndisponivelError(cep_destino)
        return frete

    @staticmethod
    def _calcular_promocao(valor_bruto: Decimal, quantidade_total: int) -> Decimal:
        if quantidade_total >= 10:
            percentual = Decimal("0.15")
        elif quantidade_total >= 5:
            percentual = Decimal("0.10")
        elif quantidade_total >= 3:
            percentual = Decimal("0.05")
        else:
            return Decimal("0.00")
        return (valor_bruto * percentual).quantize(CENT, rounding=ROUND_HALF_UP)
