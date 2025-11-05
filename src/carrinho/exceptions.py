from datetime import date

class EstoqueInsuficienteError(RuntimeError):
    def __init__(self, sku: str, solicitado: int, disponivel: int) -> None:
        mensagem = (
            f"Estoque insuficiente para SKU {sku}: solicitado {solicitado}, disponível {disponivel}."
        )
        super().__init__(mensagem)
        self.sku = sku
        self.solicitado = solicitado
        self.disponivel = disponivel


class ItemInexistenteError(LookupError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Item com SKU {sku} não está presente no carrinho.")
        self.sku = sku


class CupomExpiradoError(ValueError):
    def __init__(self, codigo: str, expira_em: date, referencia: date) -> None:
        mensagem = (
            f"Cupom {codigo} expirou em {expira_em.isoformat()} (referência {referencia.isoformat()})."
        )
        super().__init__(mensagem)
        self.codigo = codigo
        self.expira_em = expira_em
        self.referencia = referencia

class CupomInvalidoError(ValueError):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)

class FreteIndisponivelError(RuntimeError):
    def __init__(self, cep_destino: str) -> None:
        super().__init__(f"Não foi possível obter frete para o CEP {cep_destino}.")
        self.cep_destino = cep_destino
