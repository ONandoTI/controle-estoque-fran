
# Sistema de Controle de Estoque — Loja da Fran

## Sobre o projeto

O Sistema de Controle de Estoque da Loja da Fran é um MVP desenvolvido para facilitar o gerenciamento de produtos e movimentações de estoque de uma pequena loja.

O projeto busca reduzir dificuldades no controle manual, melhorar a visualização das quantidades disponíveis e auxiliar na identificação de produtos que precisam de reposição.

## Funcionalidades

- Cadastro de produtos e quantidades iniciais.
- Registro de entradas de mercadorias.
- Registro de saídas e vendas.
- Atualização automática do saldo em estoque.
- Histórico de movimentações.
- Identificação de produtos abaixo do estoque mínimo.
- Personalização do tema visual.

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Pytest
- Git e GitHub

## Como executar o projeto

1. Clone este repositório.
2. Entre na pasta do projeto.
3. Crie e ative um ambiente virtual Python.
4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Execute a aplicação:

```bash
python run.py
```

6. Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Executar os testes

Para executar os testes automatizados:

```bash
python -m pytest -v
```

## Estrutura do projeto

```text
controle-estoque-fran/
├── app/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── db.py
│   └── routes.py
├── tests/
├── .github/
│   └── workflows/
├── requirements.txt
└── run.py
```

## Objetivo

Desenvolver uma solução simples e acessível para melhorar o controle de estoque da Loja da Fran, contribuindo para a organização das atividades e a redução de problemas relacionados à falta de produtos.
