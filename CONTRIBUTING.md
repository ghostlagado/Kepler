# Contribuindo com o Kepler

Obrigado por considerar contribuir com o **Kepler**! Este documento descreve como propor melhorias, reportar problemas e manter a qualidade do projeto.

O Kepler é um sistema desktop de automação operacional e inteligência comercial, desenvolvido em Python + Flet e inicialmente orientado aos fluxos comerciais da RCHLO. A prioridade é preservar as regras de negócio validadas, reduzir tarefas manuais e manter uma arquitetura clara, testável e sustentável.

## Antes de começar

- Consulte o [README](README.md) para entender o projeto, sua arquitetura e o status da migração.
- Verifique as issues abertas para evitar trabalho duplicado.
- Para alterações que afetem regras comerciais, parsers, cálculos ou formatos de relatório, investigue primeiro o comportamento esperado e os testes existentes.
- O diretório `legacy/` e a branch `legacy` são referências históricas do PDV_V2. **Não os apague, sobrescreva ou reescreva.**
- Nunca inclua dados corporativos confidenciais, credenciais, tokens, arquivos reais de clientes/colaboradores ou relatórios restritos em commits, issues, pull requests ou testes.

## Como contribuir

### 1. Prepare o ambiente

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/ghostlagado/Kepler.git
cd Kepler
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências conforme o arquivo de dependências e as instruções atuais do projeto. Se houver divergência entre este documento e os arquivos de configuração, siga a configuração efetivamente mantida no repositório e proponha a atualização da documentação.

### 2. Crie uma branch

Use uma branch descritiva para cada mudança. Exemplos:

```bash
git switch main
git pull origin main
git switch -c feat/dashboard-filters
```

Padrões sugeridos:

- `feat/` — nova funcionalidade.
- `fix/` — correção de defeito.
- `refactor/` — reorganização interna sem alterar o comportamento esperado.
- `test/` — inclusão ou melhoria de testes.
- `docs/` — documentação.
- `chore/` — manutenção, ferramentas ou configuração.

Se estiver trabalhando em uma branch compartilhada ou com alterações locais pendentes, confira o estado do Git antes de trocar de branch ou atualizar arquivos. Não descarte trabalho existente.

### 3. Implemente a mudança

- Mantenha cada pull request focado em um objetivo.
- Prefira soluções simples, explícitas e fáceis de testar.
- Preserve a separação entre interface Flet, regras de negócio, serviços, leitura de arquivos e integrações.
- Evite duplicar cálculos ou regras comerciais.
- Não introduza dependências sem necessidade justificada.
- Não crie botões, telas ou integrações que aparentem funcionar sem uma implementação real.
- Não altere fórmulas comerciais sem verificar o comportamento legado e atualizar os testes pertinentes.
- Mantenha o tema visual **Graphite + Red** consistente com a identidade do Kepler.
- Atualize a documentação quando mudar comandos, configurações, formatos de arquivo ou comportamento funcional.

### 4. Execute os testes

Antes de abrir um pull request, execute os testes disponíveis no projeto. O conjunto atual utiliza `pytest`; confirme as instruções e dependências no repositório.

```bash
python -m pytest
```

Se a alteração envolver regras de negócio, parsers ou relatórios, inclua testes que cubram os casos relevantes, como:

- entradas válidas, vazias, incompletas ou malformadas;
- valores ausentes, zeros, arredondamentos e limites;
- totais e cálculos derivados;
- erros de leitura e gravação;
- preservação do último resultado válido quando uma nova coleta falhar.

Não declare testes aprovados sem executá-los. Se algum teste não puder ser executado, informe o motivo no pull request.

### 5. Faça commits claros

Use mensagens curtas e descritivas, preferencialmente no padrão Conventional Commits:

```text
feat: add dashboard filters
fix: preserve last valid report
refactor: isolate hourly sales calculations
test: cover department totals
docs: update setup instructions
chore: update development dependencies
```

Faça commits pequenos sempre que isso ajudar a revisar e compreender as mudanças.

### 6. Abra um pull request

Envie sua branch e abra um pull request direcionado à branch principal do projeto:

```bash
git push -u origin feat/dashboard-filters
```

O pull request deve explicar:

- **Problema:** o que motivou a alteração?
- **Solução:** o que foi implementado e por quê?
- **Escopo:** quais módulos e arquivos foram afetados?
- **Validação:** quais testes ou verificações foram executados?
- **Impactos:** há mudanças em cálculos, formatos, arquivos, configurações ou compatibilidade?
- **Interface:** quando houver mudanças visuais, inclua capturas de tela com dados fictícios ou anonimizados.

Mantenha o pull request limitado ao escopo proposto e responda aos comentários de revisão com as alterações ou justificativas necessárias.

## Diretrizes de código

### Python

- Siga o PEP 8 e utilize nomes claros e consistentes.
- Prefira type hints nas funções e interfaces entre módulos.
- Separe regras de negócio dos componentes visuais.
- Trate erros de forma explícita; evite exceções silenciosas.
- Evite funções ou classes excessivamente grandes.
- Não mantenha caminhos locais, senhas ou tokens diretamente no código.

### Flet e interface

- Reutilize componentes e estilos quando fizer sentido.
- Mantenha consistência de espaçamento, tipografia, cores e navegação.
- Apresente estados de carregamento, ausência de dados e falha quando aplicáveis.
- Evite bloquear a interface durante tarefas demoradas.
- Não exiba dados de demonstração como se fossem dados reais.

### Dados e regras comerciais

- Preserve os arquivos brutos necessários à auditoria.
- Valide dados antes de processá-los.
- Não substitua resultados válidos por resultados incompletos ou inválidos.
- Documente mudanças em fórmulas, agrupamentos, arredondamentos e critérios de filtragem.
- Utilize dados sintéticos nos testes sempre que possível.

## Reportar bugs

Ao abrir uma issue de bug, inclua:

1. Um título objetivo.
2. O comportamento observado.
3. O comportamento esperado.
4. Passos para reproduzir o problema.
5. Sistema operacional e versão do Python, quando relevantes.
6. Logs ou mensagens de erro devidamente sanitizados.
7. Um exemplo mínimo com dados fictícios, se o problema depender de um arquivo de entrada.

Não anexe relatórios corporativos reais, dados pessoais, credenciais ou capturas com informações confidenciais.

## Sugerir funcionalidades

Uma boa proposta explica:

- qual problema operacional existe;
- quem é afetado e em qual situação;
- como o processo é realizado atualmente;
- qual resultado se espera obter;
- quais regras, integrações ou limitações precisam ser consideradas.

Propostas devem priorizar redução de trabalho manual, confiabilidade dos dados, clareza dos indicadores e facilidade de manutenção. Funcionalidades genéricas para outras empresas podem ser consideradas, mas não devem comprometer o objetivo inicial do Kepler nem introduzir abstrações prematuras.

## Segurança e informações corporativas

- Nunca envie segredos ou credenciais para o Git.
- Não tente contornar controles de acesso de sistemas corporativos.
- Utilize integrações e métodos de coleta autorizados.
- Não envie mensagens reais ou execute automações externas durante testes sem autorização e configuração apropriadas.
- Se encontrar uma vulnerabilidade, não publique detalhes exploráveis em uma issue pública. Entre em contato com o mantenedor de forma privada.

## Checklist antes de enviar

- [ ] A alteração resolve um problema identificado.
- [ ] O escopo está limitado e a implementação é compreensível.
- [ ] As regras de negócio existentes foram preservadas ou suas mudanças foram justificadas.
- [ ] Os testes pertinentes foram executados.
- [ ] A documentação foi atualizada quando necessário.
- [ ] Não há credenciais, dados sensíveis ou arquivos operacionais indevidos.
- [ ] A branch `legacy` e o diretório `legacy/` permanecem intactos.
- [ ] O pull request descreve as alterações e a validação realizada.

## Obrigado

Toda contribuição que torne o Kepler mais confiável, útil e fácil de manter é bem-vinda. A prioridade é entregar automações que funcionem de verdade, preservem a integridade dos dados e resolvam problemas concretos da operação comercial.
