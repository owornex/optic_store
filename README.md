# Sodre Optic Store

Software de gestão para óticas desenvolvido pela Sodre, integrado ao ERPNext.

## Descrição

O Sodre Optic Store é um sistema completo para gestão de óticas, desenvolvido especialmente para o mercado brasileiro. Integrado ao ERPNext versão 15, oferece todas as funcionalidades necessárias para gerenciar sua ótica de forma eficiente e profissional.

### Funcionalidades Principais

* **Gestão de Prescrições**
  * Criação de prescrições ópticas com visualização gráfica
  * Registro detalhado de medidas para óculos e lentes de contato
  * Histórico completo de prescrições por cliente

* **Vendas e Atendimento**
  * Venda de óculos, lentes de contato, exames e serviços
  * Sistema de orçamentos e pedidos
  * Integração com laboratórios ópticos
  * Gestão de garantias e manutenções

* **Controle de Estoque**
  * Gestão de produtos ópticos
  * Controle de armações, lentes e acessórios
  * Transferências entre lojas
  * Rastreamento de produtos em laboratório

* **Financeiro**
  * Controle de pagamentos e recebimentos
  * Gestão de convênios e planos
  * Sistema de comissionamento
  * Relatórios financeiros detalhados

* **Fidelização**
  * Programa de pontos
  * Cartões presente
  * Gestão de descontos
  * Comunicação com clientes via SMS

### Requisitos do Sistema

* ERPNext versão 15.0.0 ou superior
* Python 3.10 ou superior
* Frappe Framework 15.0.0 ou superior

### Instalação

```bash
bench get-app optic_store https://github.com/sodre/optic_store
bench --site [nome-do-site] install-app optic_store
```

### Licença

MIT
