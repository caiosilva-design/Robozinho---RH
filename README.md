# 🤖 Robô RH — Automação de Vagas no Sistema LG

Sistema de automação para abertura e cancelamento de vagas no sistema LG, composto por um **servidor FastAPI** que executa o robô Selenium e um **cliente desktop** (Tkinter) que dispara e monitora os processos remotamente.

---

## 🏗️ Arquitetura

```
Cliente (app.py)  ──HTTPS──▶  Servidor (api.py)
     Tkinter                      FastAPI
  (máquina local)             (máquina servidora)
                                      │
                                  runner.py
                                      │
                          ┌───────────┴───────────┐
                     abrir_vagas.py        cancelar_vagas.py
                          │
                    Selenium + LG Sistema
```

O cliente envia as credenciais e o tipo de processo via HTTPS para o servidor. O servidor executa o Selenium em background e expõe um endpoint `/status` que o cliente monitora em polling a cada 2 segundos.

---

## 📁 Estrutura do Projeto

```
_automacao_rh_sistema_servidor/
│
├── api.py                      # Servidor FastAPI (endpoint /executar e /status)
├── app.py                      # Cliente desktop Tkinter
├── runner.py                   # Orquestrador do processo (login + execução)
├── driver_manager.py           # Gerenciamento do WebDriver
├── utils.py                    # Envio de e-mail ao final da execução
│
├── core/
│   ├── driver.py               # Inicialização do Selenium
│   ├── login.py                # Lógica de login no sistema LG
│   └── navegacao.py            # Funções de navegação (menus, iframes, loading)
│
├── processos/
│   ├── abrir_vagas.py          # Lógica completa de abertura de vagas
│   └── cancelar_vagas.py       # Lógica completa de cancelamento de vagas
│
├── config/
│   └── settings.py             # Carregamento de variáveis de ambiente (.env)
│
├── logs/
│   └── log.py                  # Salvamento de log em arquivo
│
├── seguranca/
│   ├── gerar_cert.py           # Script para gerar certificado SSL autoassinado
│   └── app.spec                # Spec PyInstaller para empacotar o cliente
│
├── cert.pem                    # Certificado SSL (gerado localmente)
├── key.pem                     # Chave privada SSL (gerada localmente)
└── requirements.txt            # Dependências Python
```

---

## ⚙️ Pré-requisitos

- Python 3.10+
- Google Chrome instalado na máquina servidora
- ChromeDriver compatível com a versão do Chrome
- Acesso de rede entre cliente e servidor na porta `8443`

---

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/<seu-repositorio>.git
cd _automacao_rh_sistema_servidor
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
pip install fastapi uvicorn openpyxl
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (nunca commite este arquivo):

```env
SENHA_APP=sua_senha_de_acesso_ao_app

URL_LOGIN=https://...     # URL de login para cancelamento de vagas
URL_HOME=https://...      # URL home do sistema
URL_LOGIN2=https://...    # URL de login para abertura de vagas
```

### 4. Gerar certificado SSL (se necessário)

```bash
python seguranca/gerar_cert.py
```

Isso gera `cert.pem` e `key.pem` na raiz do projeto.

---

## ▶️ Execução

### Servidor (máquina que executa o Selenium)

```bash
python api.py
```

O servidor sobe em `https://0.0.0.0:8443`.

### Cliente (máquina do operador)

```bash
python app.py
```

A interface solicita uma senha de acesso ao app (definida em `SENHA_APP` no `.env`), depois exibe o painel principal.

---

## 🖥️ Interface do Cliente

| Campo | Descrição |
|---|---|
| **Usuário / Senha** | Credenciais do operador no sistema LG |
| **Data / Hora** | Agendamento opcional (executa imediatamente se vazio) |
| **Pasta de Importação** | Caminho da pasta com os arquivos `.xlsx` de entrada |
| **Abrir Vagas** | Dispara o processo de abertura |
| **Cancelar Vagas** | Dispara o processo de cancelamento |

O log de execução é exibido em tempo real no painel inferior da interface.

---

## 📂 Arquivos de Entrada (Excel)

Os arquivos devem estar na pasta de importação selecionada:

| Processo | Arquivo esperado |
|---|---|
| Abrir Vagas | `VAGAS_PARA_ABERTURA.xlsx` |
| Cancelar Vagas | `VAGAS_PARA_CANCELAR.xlsx` |

Ambos precisam de uma coluna `STATUS` (criada automaticamente se ausente). O robô atualiza o status de cada linha conforme processa.

---

## 📦 Empacotar o Cliente (.exe)

Para distribuir o cliente sem precisar do Python instalado:

```bash
pyinstaller seguranca/app.spec
```

O executável será gerado na pasta `dist/`.

---

## 🔒 Segurança

- A comunicação entre cliente e servidor usa **HTTPS com certificado autoassinado**
- O cliente ignora a verificação do certificado (`verify=False`) por ser rede interna
- A senha do app é carregada via variável de ambiente, nunca hardcoded
- As credenciais do sistema LG transitam apenas em memória e não são logadas

---

## 📋 Fluxo de Execução

```
1. Cliente envia POST /executar  →  { tipo, usuario, senha, horario_inicio, pasta }
2. Servidor inicia thread em background
3. Se agendado: aguarda até o horário definido com countdown
4. runner.py: inicializa o Chrome via Selenium
5. runner.py: faz login no sistema LG
6. runner.py: executa abrir_vagas.py ou cancelar_vagas.py
7. Ao final: salva log em arquivo + envia e-mail com resumo
8. Cliente monitora GET /status a cada 2s e exibe progresso
```

---

## 🧩 Dependências

```
selenium
python-dotenv
pandas
fastapi
uvicorn
openpyxl
```

---

## ⚠️ Observações

- O ChromeDriver deve estar acessível no PATH da máquina servidora
- Os XPaths usados no Selenium são específicos para a versão atual do sistema LG — atualize se o sistema for alterado
- O arquivo `.env` **não deve ser versionado** (adicione ao `.gitignore`)
- Os arquivos `cert.pem` e `key.pem` também **não devem ser commitados**
