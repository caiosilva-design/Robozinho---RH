# Robô RH — Automação de Vagas no Sistema LG

Automação de abertura e cancelamento de vagas no sistema LG. Um cliente desktop em Tkinter solicita e acompanha os processos, enquanto um servidor FastAPI executa o Selenium e atualiza as planilhas Excel.

## Índice

- [Recursos e arquitetura](#recursos-e-arquitetura)
- [Estrutura](#estrutura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Planilhas de entrada](#planilhas-de-entrada)
- [Execução](#execução)
- [API](#api)
- [Logs e e-mail](#logs-e-e-mail)
- [Empacotamento](#empacotamento)
- [Limitações atuais](#limitações-atuais)
- [Segurança e dados](#segurança-e-dados)
- [Verificação e diagnóstico](#verificação-e-diagnóstico)

## Recursos e arquitetura

| Componente | Responsabilidade |
|---|---|
| Cliente Tkinter | Senha de acesso local, credenciais do LG, pasta e agendamento |
| API FastAPI | Recebe pedidos HTTPS e inicia uma thread por solicitação |
| Runner | Inicializa o Chrome, faz login e escolhe a rotina |
| Selenium | Preenche requisições ou cancela vagas no LG |
| Planilhas | Entrada dos lotes e retorno por linha |
| Monitoramento | Consulta do status global a cada 2 segundos |

O cliente envia o caminho da pasta, não o arquivo Excel. A pasta precisa estar acessível na máquina servidora, pelo usuário que executa a API. O agendamento aguarda em memória e não sobrevive ao reinício do servidor.

## Estrutura

| Arquivo / pasta | Uso |
|---|---|
| `api.py` | Rotas de execução/status e inicialização HTTPS na porta 8443 |
| `app.py` | Interface desktop e monitoramento |
| `runner.py` | Login, escolha do processo e resumo final |
| `driver_manager.py` | Fallback para obter ChromeDriver no Windows |
| `core/driver.py` | Inicialização do Chrome anônimo e maximizado |
| `core/login.py` | Autenticação e escolha da URL conforme o processo |
| `core/navegacao.py` | Navegação, menus, iframes e esperas |
| `processos/abrir_vagas.py` | Abertura e retorno das requisições |
| `processos/cancelar_vagas.py` | Cancelamento e observação |
| `config/settings.py` | URLs carregadas do ambiente |
| `utils.py` | Envio SMTP do resumo |
| `segurança/gerar_cert.py` | Geração local de certificado autoassinado |
| `segurança/app.spec` | Especificação PyInstaller do cliente |
| `requirements.txt` | Lista parcial das dependências |

A pasta real é `segurança`, com acento.

### Pendência para iniciar o servidor

`runner.py` importa `salvar_log` de `logs.log`, mas `logs/log.py` não está presente na árvore examinada. É necessário restaurar ou implementar esse módulo antes de iniciar a API. A função é chamada como `salvar_log(resumo)`.

Esta atualização documenta a condição atual; não modifica o código de execução.

## Instalação

Requisitos: Python 3.10+, Windows como ambiente previsto, Chrome na máquina servidora, Tkinter no cliente, acesso ao LG e permissão de leitura/escrita nas planilhas. O fallback do driver usa Registro do Windows e o diretório `C:/robo_rh/driver`.

No PowerShell:

```powershell
git clone https://github.com/caiosilva-design/Robozinho---RH.git
cd Robozinho---RH
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install fastapi uvicorn requests openpyxl cryptography
```

O `requirements.txt` contém apenas `selenium`, `python-dotenv` e `pandas`. As dependências complementares acima atendem aos imports da API, cliente, Excel e gerador de certificado. PyInstaller é necessário apenas para empacotar. As versões não estão fixadas no repositório atual.

## Configuração

### Ambiente do servidor

`config/settings.py` e `utils.py` usam `load_dotenv()`. Configure as variáveis no ambiente do processo ou em um `.env` privado encontrado pelo carregador.

| Variável | Uso |
|---|---|
| `URL_LOGIN` | Login para cancelamento |
| `URL_LOGIN2` | Login para abertura |
| `URL_HOME` | URL disponibilizada à navegação |
| `EMAIL` | Conta de autenticação SMTP |
| `SENHA_E` | Credencial SMTP da conta de envio |

O usuário e a senha do operador no LG são recebidos do cliente. Não coloque credenciais reais na documentação ou no repositório.

### Ambiente do cliente

O `app.py` carrega explicitamente `automacao_rh/.env` dentro do diretório do aplicativo. Quando empacotado, usa como base o diretório do executável. Configure `SENHA_APP` nesse arquivo ou no ambiente do processo.

A senha libera a interface local; ela não autentica chamadas à API.

No `app.py`, ajuste `API_URL` para o endereço HTTPS da máquina servidora e revise a lista `PASTAS`. As opções atuais utilizam unidade de rede Z. Essa unidade precisa existir no contexto da conta que executa o servidor, não apenas no computador do operador.

### Certificado

A API procura `cert.pem` e `key.pem` ao lado de `api.py`. O gerador grava os arquivos no diretório de trabalho atual:

```powershell
python "segurança/gerar_cert.py"
```

Execute a partir da raiz em uma cópia de desenvolvimento preparada: o script sobrescreve arquivos com esses nomes. Ele gera um certificado autoassinado para `localhost`, válido por 365 dias.

O cliente atual usa `verify=False`, desativando a validação da identidade do servidor. Para uma implantação confiável, configure certificado adequado ao endereço e validação no cliente.

## Planilhas de entrada

| Processo | Nome exato | Retorno |
|---|---|---|
| Abertura | `VAGAS_PARA_ABERTURA.xlsx` | `STATUS` e `NUMERO_RQ` |
| Cancelamento | `VAGAS_PARA_CANCELAR.xlsx` | `STATUS` |

O robô sobrescreve o arquivo de entrada ao salvar o retorno. Faça backup e feche o arquivo no Excel antes de executar.

### Abertura

A rotina usa a primeira planilha e posições com `df.iloc`, não os nomes dos cabeçalhos. Preserve a ordem e mantenha as colunas de retorno depois dos campos de entrada.

| Coluna | Índice | Conteúdo usado |
|---|---:|---|
| A | 0 | Matrícula do gestor |
| B | 1 | Motivo da requisição |
| C | 2 | Empresa |
| D | 3 | Código da posição |
| E | 4 | Matrícula para substituição |
| F | 5 | Nome usado no fluxo de movimentação |
| G | 6 | Quantidade de vagas |
| H | 7 | Descrição/título |
| I | 8 | Tipo de contrato |
| J | 9 | Não utilizado diretamente; preserve a posição |
| K | 10 | Observação |
| L | 11 | Salário |
| M | 12 | Escala |
| N | 13 | Categoria |

Tipos de contrato mapeados: EFETIVO, ESTAGIÁRIO, TEMPORÁRIO, TERCEIRO, TRAINEE, PESSOA JURÍDICA, APRENDIZ, INTERMITENTE e as duas opções VERDE E AMARELO do código. Campo vazio é ignorado.

A categoria mapeada atualmente é `Estágio/Jovem/Assistencial/Operacional`. Outros valores exigem alteração no mapeamento. Fluxos de substituição e movimentação dependem do texto do motivo; confira os valores aceitos no código e no LG.

A rotina cria `STATUS` e `NUMERO_RQ` se ausentes. `STATUS` recebe `OK` ou `ERRO`. `NUMERO_RQ` guarda o texto do retorno de criação ou a indicação da etapa com erro; pode não conter apenas números.

### Cancelamento

| Coluna | Conteúdo |
|---|---|
| A | Código da vaga/processo usado no filtro |
| B | Observação do cancelamento |

Sem segunda coluna, é usada uma observação padrão. O retorno é `CANCELADO` ou `ERRO`, com até duas tentativas por registro. A leitura não força todos os campos para texto; confira códigos com zeros iniciais.

### Reexecução

As duas rotinas percorrem as linhas sem filtrar as que já têm sucesso em `STATUS`. Reenviar o mesmo arquivo pode repetir ações. Separe pendências e confira o estado real no LG antes de repetir um lote interrompido.

## Execução

Antes de iniciar, resolva o módulo de logs ausente e configure dependências, URLs, certificados e pastas.

Na máquina servidora:

```powershell
python api.py
```

O servidor escuta em todas as interfaces na porta 8443. `0.0.0.0` é o endereço de escuta; o cliente deve usar o IP ou nome real da máquina.

Na máquina do operador:

```powershell
python app.py
```

1. Informe a senha de acesso local.
2. Preencha as credenciais do LG.
3. Selecione a pasta.
4. Deixe data/hora vazias ou use `DD/MM/AAAA` e `HH:MM` para agendar.
5. Escolha abertura ou cancelamento.
6. Acompanhe as mensagens e confira cada retorno na planilha e no sistema.

O agendamento usa o relógio do servidor e não é persistente. Cliente e servidor precisam ter relógios e fusos alinhados. Execute um lote por vez: a API não bloqueia solicitações concorrentes e compartilha o mesmo status global.

## API

| Método e rota | Uso |
|---|---|
| `POST /executar` | Recebe a solicitação e inicia uma thread |
| `GET /status` | Retorna `status`, `log` e `progresso` globais |

Campos do pedido:

| Campo | Conteúdo |
|---|---|
| `tipo` | `abrir` ou `cancelar` |
| `usuario`, `senha` | Credenciais do operador |
| `horario_inicio` | `null` ou data ISO sem fuso, como `2030-01-15T08:30:00` |
| `pasta` | Caminho acessível na máquina servidora |

A confirmação de recebimento não significa que as vagas foram processadas. Horário inválido retorna um objeto com `erro`; o cliente atual não verifica explicitamente esse retorno antes de monitorar. Não existem rotas para upload de planilha, parada, cancelamento de agendamento ou consulta por ID de execução.

## Logs e e-mail

O runner monta um resumo e chama `salvar_log(resumo)`. O destino do log depende do módulo ausente `logs.log`.

O SMTP usa `smtp.gmail.com:587` com STARTTLS e as variáveis `EMAIL` e `SENHA_E`. O destinatário está fixado em `utils.py`; revise-o antes de usar em outro ambiente.

As rotinas salvam a planilha na pasta de importação, mas o runner procura o anexo em **Downloads** do usuário do servidor. O e-mail pode sair sem a planilha atualizada ou anexar outro arquivo com o mesmo nome existente nessa pasta.

A mensagem final indica encerramento, não sucesso de todas as linhas. Uma falha ao salvar o log também pode impedir e-mail e sinalização final.

## Empacotamento

```powershell
python -m pip install pyinstaller
python -m PyInstaller "segurança/app.spec"
```

Confira os caminhos antes do build: o spec está em subpasta e referencia `app.py`. Ajuste a referência e o diretório de trabalho se necessário. O spec não inclui arquivos de dados; distribua a configuração privada separadamente em `automacao_rh/.env`, ao lado do executável.

O executável é o cliente. Servidor, Chrome, credenciais e acesso às planilhas continuam necessários na máquina de automação.

## Limitações atuais

- O módulo `logs.log` está ausente e as dependências estão incompletas no `requirements.txt`.
- Não há fila persistente, isolamento por usuário ou bloqueio global de execução.
- A abertura tem lógica de reautenticação, mas o runner não repassa usuário/senha aos parâmetros opcionais da rotina; não conte com recuperação automática funcional sem ajuste.
- O WebDriver é inicializado antes do bloco principal de tratamento; falha nessa etapa pode deixar o cliente sem sinalização final.
- O runner não chama `driver.quit()` explicitamente.
- O progresso representa a posição da linha, não o percentual de operações confirmadas.
- O cancelamento marca sucesso após as interações, sem consulta independente de confirmação final.
- XPaths, iframes, textos e esperas dependem da versão e configuração do LG.
- O login contém verificações de URL específicas do ambiente de origem.
- O fallback de driver depende do Windows e de diretório fixo.
- Não há modo de simulação ou configuração headless.

É uma automação desktop/servidor; não é um site estático para Pages nem um serviço preparado para hospedagem serverless.

## Segurança e dados

A API não exige autenticação própria em `/executar` ou `/status`. A senha local não protege esses endpoints. Restrinja acesso de rede e implemente autenticação/autorização no servidor para uso compartilhado.

O repositório público contém arquivos chamados `key.pem` e `cert.pem`. A chave privada não foi lida nesta revisão. **Se foram utilizados em algum ambiente, substitua a chave e o certificado e retire o material privado do versionamento, incluindo o histórico quando aplicável.**

O cliente e partes do download de driver desativam a validação TLS. Isso descreve a implementação atual, não uma configuração recomendada de produção.

Planilhas, logs e resumos podem conter dados de RH, identificadores, salários e informações operacionais. Não publique arquivos reais nem credenciais. Excluir o campo de senha da serialização Pydantic não autentica pedidos nem protege todas as partes da aplicação.

## Verificação e diagnóstico

Nenhum lote foi executado no LG nesta atualização. A alteração é exclusivamente de documentação e não remove os emojis das mensagens existentes no código.

Não há suíte de testes automatizados indicada no repositório. Valide em ambiente autorizado, com um lote pequeno conferido, incluindo login, caminhos, ordem das colunas, retorno real no LG, e-mail, interrupção e reexecução.

| Sintoma | O que conferir |
|---|---|
| `No module named logs` | Restaurar ou implementar `logs/log.py` |
| Imports de API/cliente/Excel falham | Instalar dependências complementares |
| Senha local não funciona | `SENHA_APP` e caminho `automacao_rh/.env` |
| Cliente não conecta | `API_URL`, rede, porta e servidor ativo |
| Erro de arquivo ou permissão | Pasta na máquina servidora e arquivo fechado no Excel |
| Chrome não inicia | Instalação, versão do driver e permissão no diretório de fallback |
| Login não conclui | URLs, seletores, credenciais e redirecionamento |
| Preenchimento falha | Ordem das colunas, motivo e valores aceitos |
| E-mail sem anexo | Diferença entre pasta de importação e Downloads |
| Cliente permanece aguardando | Falha inicial, módulo de logs ou ausência de sinalização final |
| Lote já concluído será repetido | Separar pendências; as rotinas não pulam sucessos automaticamente |

## Licença

Não foi identificada uma licença de uso nos arquivos examinados. Esta documentação não atribui uma licença nova ao projeto.
