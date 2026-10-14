# Automação Comercial — PDV V2

Aplicação desktop desenvolvida em **Python** para automatizar rotinas operacionais baseadas em planilhas Excel. O sistema reúne ferramentas de processamento de informações comerciais em uma interface gráfica, reduzindo tarefas manuais e padronizando atualizações.

> **Contexto:** o código disponível indica um projeto originalmente desenvolvido para apoiar rotinas internas da RCHLO S.A. Este README descreve funcionalidades identificadas no código, sem pressupor recursos não implementados.

## ✨ Funcionalidades

- **Hora a Hora (HxH):** processa informações inseridas na interface e atualiza a planilha de acompanhamento.
- **Participação (PA):** interpreta dados operacionais e preenche os campos previstos na planilha parcial.
- **Vendas com Juros (VJ):** processa informações de vendas e valores associados para atualizar a planilha de controle.
- **E-Store:** consolida valores de metas a partir de planilhas e atualiza os dados usados nessa rotina.
- **Metas comerciais:** consulta metas por data, filial e grupo de produtos.
- **Autenticação:** tela de login integrada a um serviço Firebase Realtime Database.
- **Área administrativa:** a interface inclui opções de gerenciamento de usuários, senha e nome, condicionadas ao usuário administrador.

## 🧰 Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

- **Interface gráfica:** PyQt5 com telas `.ui`.
- **Planilhas:** `openpyxl`.
- **Tema visual:** `qdarktheme`.
- **Comunicação HTTP:** `requests`.
- **Autenticação remota:** Firebase Realtime Database.

## 📁 Organização esperada

A aplicação utiliza arquivos Python, interfaces gráficas e planilhas organizados por diretórios. Entre os caminhos referenciados no código estão:

```text
PDV_V2/
├── main.py                 # Inicialização e navegação
├── metas.py                # Consulta de metas comerciais
├── hxh.py                  # Processamento Hora a Hora
├── pa.py                   # Processamento de Participação
├── vj.py                   # Processamento de Vendas com Juros
├── estore.py               # Consolidação de dados E-Store
├── atualizarEstore.py      # Atualização da planilha E-Store
├── uic/                    # Interfaces gráficas Qt (.ui)
├── pln/                    # Planilhas usadas pelas rotinas
├── metas/                  # Arquivos de metas comerciais
└── txt/                    # Arquivos temporários de entrada
```

A estrutura acima resume os caminhos referenciados pelo código; a presença de todos os arquivos depende da versão e da configuração local.

## 🚀 Configuração e execução

### Pré-requisitos

- Python 3.9 ou superior, compatível com as dependências do projeto.
- Pip.
- Arquivos de planilhas e interfaces necessários às rotinas.
- Acesso ao Firebase configurado para o mecanismo de autenticação utilizado.

### 1. Clone o repositório

```bash
git clone https://github.com/foxtec198/PDV_V2.git
cd PDV_V2
```

### 2. Crie e ative um ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências principais

```bash
python -m pip install --upgrade pip
python -m pip install PyQt5 QDarkTheme requests openpyxl
```

> Dependências adicionais podem ser necessárias conforme os módulos e arquivos da versão utilizada. Valide a execução em ambiente de desenvolvimento antes de distribuir a aplicação.

### 4. Execute a aplicação

Na raiz do projeto, com os arquivos necessários presentes:

```bash
python main.py
```

## 📊 Arquivos de entrada e saída

As rotinas dependem de planilhas e arquivos locais específicos, incluindo:

- `metas/metas.xlsx` — base de metas comerciais.
- `pln/horaxhora.xlsx` — planilha da rotina Hora a Hora.
- `pln/parcial.xlsx` — planilha da rotina Participação.
- `pln/vj.xlsx` — planilha da rotina Vendas com Juros.
- `pln/estore.xlsx` — planilha da rotina E-Store.
- `txt/` — arquivos temporários usados para transferir os dados informados na interface aos módulos.

Mantenha os nomes e caminhos compatíveis com as referências do código ou ajuste-os em conjunto. Faça cópias de segurança das planilhas antes de executar rotinas que gravam alterações.

## 🔐 Segurança e manutenção

- Não armazene senhas, tokens ou credenciais em arquivos versionados.
- Revise as regras de autenticação e as permissões do Firebase antes de disponibilizar o sistema em outros ambientes.
- Evite compartilhar dados comerciais e pessoais reais em issues, commits ou capturas de tela.
- Valide os arquivos de entrada e mantenha cópias de segurança das planilhas originais.

## 🛣️ Evolução do projeto

Melhorias técnicas possíveis:

- Centralizar as dependências em um arquivo `requirements.txt`.
- Externalizar configurações e identificadores de filial.
- Substituir caminhos relativos frágeis por caminhos resolvidos a partir da raiz do projeto.
- Melhorar o tratamento de erros e os registros de execução.
- Criar testes automatizados para o processamento e a atualização das planilhas.
- Documentar o empacotamento e a distribuição para Windows.

## 👨‍💻 Autoria

Desenvolvido por **Guilherme Barbosa André Breve — TecnoBreve**.

---

<p align="center">Projeto de automação comercial desenvolvido em Python.</p>