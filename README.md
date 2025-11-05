# Trabalho N2 — Cenário B 

Este repositório representa a implementação do cenário B descrito nas orientações da disciplina de Teste de Software: catálogo de produtos, carrinho de compras, regras de promoção, cupom e cálculo de frete. Toda a solução foi desenvolvida em Python com foco nos critérios de avaliação do trabalho, exceto a configuração de CI/CD que foi omitida.

## Estrutura de pastas

```
pytest.ini
src/
  carrinho/
    __init__.py
    entities.py
    exceptions.py
    frete.py
    repositories.py
    services.py
tests/
  conftest.py
  test_carrinho_service.py
  test_desempenho.py
  test_excecoes.py
  test_fluxo_integracao.py
  test_promocoes_parametrizado.py
```

## Ambiente e dependências

1. Crie e ative um ambiente virtual.
2. Instale as dependências de desenvolvimento:
   ```bash
   pip install -r requirements.txt
   ```

## Execução de testes

- Rodar toda a suíte: `pytest`
- Pular testes lentos: `pytest -m "not slow"`
- Medir cobertura (linhas e ramos):
  ```bash
  coverage run -m pytest
  coverage html  # gera htmlcov/index.html
  coverage report
  ```
