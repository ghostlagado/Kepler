# Kepler

Sistema desktop de automação operacional e inteligência comercial da RCHLO,
reconstruído a partir do **PDV_V2** (PyQt5) em **Python + Flet**. O código
legado está preservado, intacto, em `legacy/` e na branch `legacy`.

O projeto mantém as rotinas identificadas no legado — Hora a Hora,
Participação, Vendas com Juros, E-Store e consulta de metas comerciais — e
adota uma arquitetura em camadas em que as regras de negócio são testáveis
sem depender da interface.

## Status da migração

| Módulo | Status |
| --- | --- |
| Hora a Hora | **Fluxo funcional** (processamento, tela, exportação XLSX, Dashboard) |
| Vendas com Juros | Pendente (regras mapeadas no legado: `legacy/vj.py`) |
| E-Store | Pendente (`legacy/estore.py`, `legacy/atualizarEstore.py`) |
| Vendas por Colaborador / Participação | Pendente (`legacy/pa.py`) |
| Login Firebase / administração de usuários | Pendente (decisão: não migrar sem demanda) |
| Envio automático ao WhatsApp | Não implementado — será uma **API separada**, integrada depois |

A coleta continua manual por design: o relatório de DCOs é copiado do sistema
corporativo e colado (ou carregado de arquivo TXT), como no PDV_V2. Não há
automação de navegador porque o legado não a possuía.

## ✨ Funcionalidades

- **Hora a Hora (HxH):** cola o relatório bruto de DCOs, processa, exibe a
  tabela por departamento (meta, realizado, gap, % da meta, ordenável) e
  exporta planilha compatível com o histórico `horaxhora.xlsx`.
- **Dashboard:** cartões de meta/realizado/gap por loja, gráfico de barras
  realizado × meta por departamento e curva de evolução das coletas do dia,
  com seletor de loja (todas as 17 lojas E-Store).
- **Metas comerciais:** consulta por data, filial (Local) e grupo de operações.
- **Preservação de dados:** uma coleta com erro nunca sobrescreve o último
  relatório válido (snapshot com escrita atômica + histórico em JSONL).

As rotinas PA/VJ/E-Store existem no legado e ainda não foram migradas; veja a
tabela de status.

## 🧰 Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-132A64?style=for-the-badge&logo=flutter&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

- **Interface gráfica:** Flet (desktop e web) com tema escuro próprio
  (paleta "Graphite + Red"), incluindo `flet-charts` nos gráficos do Dashboard.
- **Planilhas:** `openpyxl` (leitura de metas e exportação XLSX).
- **Testes:** `pytest` cobrindo domínio e serviços, sem tocar na UI.
- **Legado (referência em `legacy/`):** PyQt5, `qdarktheme`, `requests`,
  Firebase Realtime Database para autenticação.

## 📁 Estrutura

```text
src/
├── main.py            # ponto de entrada Flet
├── core/              # config de caminhos, paleta Graphite + Red, tema
├── domain/            # departamentos/DCOs, cálculo do relatório, leitura de metas
├── parsers/           # parser do texto bruto de DCOs (regra de posição por nº de palavras)
├── services/          # pipeline: validar → processar → snapshot/histórico
├── reports/           # exportação compatível com horaxhora.xlsx
└── ui/                # shell com navegação lateral, Dashboard e Hora a Hora
scripts/
└── demo_simulator.py  # gerador de dados DEMO (100% fictícios)
tests/                 # pytest: parsers, domínio, serviço, relatórios
data/                  # (gitignored) brutos, snapshot, histórico e exportações
metas/                 # (gitignored) metas/metas.xlsx
legacy/                # PDV_V2 intacto para referência
```

No legado, a organização correspondia a `main.py`, `hxh.py`, `pa.py`, `vj.py`,
`estore.py`, `metas.py` mais as pastas `uic/` (telas `.ui`), `pln/`, `metas/`
e `txt/` — tudo preservado dentro de `legacy/`.

## 📊 Arquivos de entrada e saída

- `metas/metas.xlsx` — base de metas comerciais (layout do PDV_V2: colunas
  Data, Local, Grupo Operações, Meta; leitura a partir da linha 4).
- Entrada Hora a Hora — texto bruto do relatório de DCOs, colado na interface
  ou carregado de um `.txt` arquivado em `data/raw/hora_a_hora/`.
- `data/hora_a_hora_snapshot.json` — último relatório válido (escrita atômica).
- `data/hora_a_hora_history.jsonl` — uma linha por coleta válida; alimenta a
  curva do Dashboard e o seletor de loja.
- `data/exports/hora_a_hora_*.xlsx` — exportação compatível com a planilha
  histórica (dados a partir da linha 7, fórmula `=E-C` para o gap).

Faça cópias de segurança das planilhas antes de rodar rotinas que gravam
alterações, como no legado.

## 🔑 Regras de negócio herdadas (Hora a Hora)

- Gap = Realizado − Meta do dia (fórmula `=E-C` da planilha histórica).
- Total loja = soma dos departamentos.
- Metas por data + loja + grupo de operações (`Perfumaria`→Beleza,
  `Eletrônicos`→Tecnologia, `Infanto-Juvenil`→Infantil,
  `Óculos e Bijuteria`→Óculos e Bijuterias).
- Valor por DCO localizado pela contagem de palavras da linha
  (10→5, 11→6, 12→7, 13→8, 14→5, 15→6, 16→7, 17→8), com `.` como milhar e
  `,` como decimal.
- Linha de formato não reconhecido aborta a coleta e mantém o último
  relatório válido.
- Classificação visual: abaixo da meta (vermelho), 100–105% (âmbar),
  acima de 105% (verde).

## 🚀 Ambiente e execução

Requer Python ≥ 3.10 (o legado exigia ≥ 3.9 com PyQt5).

```bash
python -m venv venv
venv/bin/pip install -e .          # ou: pip install flet flet-charts openpyxl
venv/bin/flet run src/main.py      # desktop
```

Coloque a planilha de metas em `metas/metas.xlsx`. Sem a planilha ou sem
dados reais, use o modo DEMO abaixo.

## 🎭 Modo DEMO (dados fictícios)

Sem acesso ao sistema corporativo, o app pode rodar com números simulados que
crescem a cada hora — curva intradiária de shopping, fator próprio por
loja/departamento, determinísticos por (data, loja, hora). **Todos os valores
são 100% fictícios e servem apenas para apresentação:**

```bash
venv/bin/python scripts/demo_simulator.py --backfill   # dia completo até a hora atual
venv/bin/python scripts/demo_simulator.py --loop       # deixa rodando: 1 coleta nova por hora
```

O app detecta a nova coleta sozinho e atualiza Dashboard/Hora a Hora em até
60 segundos. Cada coleta válida alimenta o histórico
(`data/hora_a_hora_history.jsonl`), usado pela curva de evolução e pelo
seletor de loja (as 17 lojas E-Store têm coletas simuladas). Para zerar o
demo: `rm -rf data/ metas/` (ambos gitignored; o `metas/metas.xlsx` real fica
preservado em `legacy/metas/` e no histórico do git).

## 🧪 Testes

```bash
venv/bin/python -m pytest -q
```

Cobrem parser de DCOs, agregação por departamento, gap/status/totais,
leitura de metas, histórico/snapshot e preservação do último relatório
válido em coletas inválidas.

## 🔐 Segurança e manutenção

- Não armazene senhas, tokens, chaves ou credenciais em arquivos versionados;
  nada de informação sensível nos logs.
- Não envie mensagens reais (ex.: WhatsApp) em testes sem autorização.
- Não apresente dados fictícios do modo DEMO como se fossem reais.
- Evite compartilhar dados comerciais ou pessoais reais em issues, commits ou
  capturas de tela.
- A pasta `legacy/` e a branch `legacy` são histórico preservado: nunca
  sobrescrever, excluir ou reescrever o histórico do legado.

## ⚠️ Limitações conhecidas

- Validação numérica contra o legado foi feita com dados de exemplo (os TXT
  históricos do repo estavam vazios); conferir contra um dia real antes do uso.
- Envio ao WhatsApp depende da API separada planejada; até lá, a entrega do
  relatório continua manual.
- Processamento roda no thread principal (abertura de `metas.xlsx` ~1s);
  mover para background quando houver agendamento.

## 🛣️ Evolução

O legado listava como melhorias desejáveis: centralizar dependências (feito —
`pyproject.toml`), externalizar configurações e caminhos (feito — `src/core/config.py`),
melhorar tratamento de erros (feito — pipeline com erros nomeados por linha),
testes automatizados (feito) e documentar empacotamento. Próximos passos:
API de envio WhatsApp, migração de PA/VJ/E-Store e agendamento de coletas.

## 👨‍💻 Autoria

Desenvolvido por **Guilherme Barbosa André Breve — TecnoBreve**.

---

<p align="center">Projeto de automação comercial desenvolvido em Python.</p>
