import os
import pandas as pd
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from core.navegacao import abrir_abertura_vagas, reentrar_iframe, SessaoExpiradaError


# =========================
# 📥 EXCEL
# =========================
def carregar_excel(pasta=r"Z:\PROCESSOS\Importacao"):
    caminho = pasta + r"\VAGAS_PARA_ABERTURA.xlsx"

    df = pd.read_excel(caminho, dtype=str)

    if 'STATUS' not in df.columns:
        df['STATUS'] = ''

    if 'NUMERO_RQ' not in df.columns:
        df['NUMERO_RQ'] = ''

    return df, caminho

# =========================
# ⏳ WAIT LG
# =========================
def wait_for_page_load(driver):
    WebDriverWait(driver, 100).until(
        EC.invisibility_of_element_located((By.XPATH,
        '/html/body/div[1]/div[2]/div/div/div/div[1]'))
    )

# =========================
# 👤 GESTOR
# =========================
def selecionar_gestor(driver, matricula):
    wait = WebDriverWait(driver, 60)

    btn = wait.until(
        EC.presence_of_element_located((By.ID, "lg_cabecalho_processo_toolbar_selecaoColaborador"))
    )

    print(f"👤 Selecionando gestor {matricula}")

    btn.click()
    sleep(20)

    campo = wait.until(EC.element_to_be_clickable((By.XPATH,
    '/html/body/div[4]/div[2]/div[2]/div[1]/div[1]/div/input')))
    campo.send_keys(str(matricula))

    # ⏳ Aguarda o loading sumir antes de clicar no botão de busca
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "lg-aa-loading__container__painel"))
    )

    try:
        driver.find_element(By.XPATH,
        '/html/body/div[4]/div[2]/div[2]/div[1]/div[2]/a').click()
    except Exception:
        print("⚠️ Click no botão de busca interceptado — tentando via JS...")
        btn_busca = driver.find_element(By.XPATH,
        '/html/body/div[4]/div[2]/div[2]/div[1]/div[2]/a')
        driver.execute_script("arguments[0].click();", btn_busca)

    sleep(5)

    resultado = wait.until(EC.element_to_be_clickable((By.XPATH,
    f"//ul/li[contains(text(), '{matricula}')]")))

    try:
        resultado.click()
        resultado.click()
    except Exception:
        print("⚠️ Click no resultado interceptado — tentando via JS...")
        driver.execute_script("arguments[0].click();", resultado)
        driver.execute_script("arguments[0].click();", resultado)

    print("✅ Gestor OK")

# Motivos que usam fluxo de Substituição com desligamento
MOTIVOS_SUBSTITUICAO_DESLIGAMENTO = ["Substituição - Desligamento - Efetivo", "Substituição - Rescisão - Efetivo"]


# =========================
# 📌 MOTIVO
# =========================
def selecionar_motivo(driver, motivo):
    wait = WebDriverWait(driver, 60)

    print("📌 Selecionando motivo...")

    campo = wait.until(EC.element_to_be_clickable((By.XPATH,
    '/html/body/div[2]/form/div/div[9]/div/div/div[2]/div/div/div[1]/div/span/span[1]')))
    campo.click()

    input_busca = wait.until(EC.element_to_be_clickable((By.XPATH,
    '/html/body/div[2]/form/div/div[9]/div/div/div[2]/div/div/div[1]/div/span[2]/span/span[1]/input')))
    input_busca.send_keys(str(motivo))

    wait.until(lambda d: len(d.find_elements(By.XPATH,
    '/html/body/div[2]/form/div/div[9]/div/div/div[2]/div/div/div[1]/div/span[2]/span/span[2]/ul/li')) == 1)

    driver.find_element(By.XPATH,
    '/html/body/div[2]/form/div/div[9]/div/div/div[2]/div/div/div[1]/div/span[2]/span/span[2]/ul/li').click()

    # ⏳ Aguarda o dropdown fechar
    wait.until(EC.invisibility_of_element_located((By.XPATH,
    '/html/body/div[2]/form/div/div[9]/div/div/div[2]/div/div/div[1]/div/span[2]/span')))

    # ⏳ Aguarda o re-render da página após seleção do motivo (LG recarrega campos dinâmicos)
    wait_for_page_load(driver)
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "lg-aa-loading__container__painel"))
    )

    sleep(3)

    print("✅ Motivo OK")


# =========================
# 🏢 EMPRESA
# =========================
def preencher_empresa(driver, num_empresa, motivo_requisicao):
    wait = WebDriverWait(driver, 60)

    print("🏢 Empresa...")

    wait_for_page_load(driver)
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "lg-aa-loading__container__painel"))
    )

    sleep(3)

    if any(m in str(motivo_requisicao) for m in MOTIVOS_SUBSTITUICAO_DESLIGAMENTO):
        aria_id = "select2-DadosDaRequisicao_ColaboradorSubstituido_CodEmpresa-container"
    else:
        aria_id = "select2-DadosDaRequisicao_DadosContratuais_CodigoEmpresaEscolhida-container"

    campo = wait.until(EC.element_to_be_clickable((By.XPATH,
    f'//span[@aria-labelledby="{aria_id}"]')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
    sleep(1)

    actions = ActionChains(driver)
    actions.move_to_element(campo).click().perform()

    input_busca = wait.until(EC.visibility_of_element_located((By.XPATH,
    '//span[contains(@class,"select2-dropdown")]//input[contains(@class,"select2-search__field")]')))

    input_busca.send_keys(str(num_empresa))
    sleep(4)

    opcao = wait.until(EC.element_to_be_clickable((By.XPATH,
    '//li[contains(@class,"select2-results__option") and not(contains(@class,"select2-results__option--disabled"))]')))

    actions2 = ActionChains(driver)
    actions2.move_to_element(opcao).click().perform()
 
    print("🏢 Empresa Ok")

# =========================
# 📌 POSIÇÃO
# =========================
def preencher_posicao(driver, cod_posicao, motivo_requisicao):
    wait = WebDriverWait(driver, 60)

    print("📌 Posição...")
    wait_for_page_load(driver)
    sleep(1)

    if any(m in str(motivo_requisicao) for m in MOTIVOS_SUBSTITUICAO_DESLIGAMENTO):
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        'button.lg-aa-botao-campoComFiltro')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        sleep(1)
        actions = ActionChains(driver)
        actions.move_to_element(btn).click().perform()

        sleep(2)

        campo = wait.until(EC.visibility_of_element_located((By.ID, 'Posicao_Descricao')))
        campo.send_keys(str(cod_posicao))

        sleep(2)

        driver.find_element(By.XPATH,
        '/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/div[10]/button').click()

        sleep(40)

        driver.find_element(By.XPATH,
        '/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/div[12]/div/div/table/tbody/tr/td[3]/button').click()

    else:
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        'button.botaoPesquisePosicao')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        sleep(1)
        actions = ActionChains(driver)
        actions.move_to_element(btn).click().perform()

        sleep(2)

        campo = wait.until(EC.visibility_of_element_located((By.ID, 'Posicao_Descricao')))
        campo.send_keys(str(cod_posicao))

        sleep(2)

        driver.find_element(By.XPATH,
        '/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/div[10]/button').click()

        sleep(40)

        driver.find_element(By.XPATH,
        '/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/div[12]/div/div/table/tbody/tr/td[3]/button').click()

    print("📌 Posição OK")

# =========================
# 👤 SUBSTITUTO
# =========================
def preencher_substituto(driver, matricula, motivo_requisicao, nome_substituto=None):
    wait = WebDriverWait(driver, 60)

    print("👤 Substituto...")

    if any(m in str(motivo_requisicao) for m in MOTIVOS_SUBSTITUICAO_DESLIGAMENTO):
        campo = wait.until(EC.element_to_be_clickable((By.XPATH,
        '//span[@aria-labelledby="select2-DadosDaRequisicao_ListaDeColaboradoresSubstituidos_0__PessoaID-container"]')))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
        sleep(1)

        actions = ActionChains(driver)
        actions.move_to_element(campo).click().perform()

        input_busca = wait.until(EC.visibility_of_element_located((By.XPATH,
        '//span[contains(@class,"select2-dropdown")]//input[contains(@class,"select2-search__field")]')))
        input_busca.send_keys(str(matricula))
        sleep(3)

        opcao = wait.until(EC.element_to_be_clickable((By.XPATH,
        '//li[contains(@class,"select2-results__option") and not(contains(@class,"select2-results__option--disabled"))]')))

        actions2 = ActionChains(driver)
        actions2.move_to_element(opcao).click().perform()

    elif "Movimentações" in str(motivo_requisicao):
        # 👤 Matrícula
        campo_matricula = wait.until(EC.visibility_of_element_located((By.ID,
        'DadosDaRequisicao_ListaInformacoesAdicionais_0__Valor')))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_matricula)
        sleep(1)
        actions = ActionChains(driver)
        actions.move_to_element(campo_matricula).click().perform()
        campo_matricula.clear()
        campo_matricula.send_keys(str(matricula))

        sleep(1)

        # 👤 Nome do substituto
        campo_nome = wait.until(EC.visibility_of_element_located((By.ID,
        'DadosDaRequisicao_ListaInformacoesAdicionais_1__Valor')))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_nome)
        sleep(1)
        actions2 = ActionChains(driver)
        actions2.move_to_element(campo_nome).click().perform()
        campo_nome.clear()
        campo_nome.send_keys(str(nome_substituto))

        sleep(1)

        # 📻 Selecionar radio Movimentação
        radio = wait.until(EC.presence_of_element_located((By.ID,
        'DadosDaRequisicao_ListaInformacoesAdicionais_2__Valor')))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
        sleep(1)
        driver.execute_script("arguments[0].click();", radio)

    print("👤 Substituto OK")

# =========================
# 📝 DESCRIÇÃO
# =========================
def preencher_descricao(driver, descricao):
    wait = WebDriverWait(driver, 60)

    print("📝 Descrição...")

    campo = wait.until(EC.visibility_of_element_located((By.ID,
    'DadosDaRequisicao_TituloRequisicao')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
    sleep(1)

    actions = ActionChains(driver)
    actions.move_to_element(campo).click().perform()

    campo.clear()
    campo.send_keys(str(descricao))

    print("📝 Descrição OK")


# =========================
# 📄 TIPO CONTRATO
# =========================
def preencher_tipo_contrato(driver, tipo_contrato):
    wait = WebDriverWait(driver, 60)

    print("📄 Tipo contrato...")

    # ⏭️ Pula se vazio ou nan
    if pd.isna(tipo_contrato) or str(tipo_contrato).strip() == '':
        print("⏭️ Tipo contrato vazio — pulando...")
        return

    mapa = {
        'EFETIVO': '0',
        'ESTAGIÁRIO': '1',
        'TEMPORÁRIO': '2',
        'TERCEIRO': '3',
        'TRAINEE': '4',
        'PESSOA JURÍDICA': '5',
        'APRENDIZ': '6',
        'INTERMITENTE': '7',
        'VERDE E AMARELO - SEM ACORDO': '8',
        'VERDE E AMARELO - COM ACORDO': '9',
    }

    valor = mapa.get(str(tipo_contrato).strip().upper())

    if not valor:
        raise Exception(f"Tipo contrato inválido: {tipo_contrato}")

    select = wait.until(EC.presence_of_element_located((By.ID,
    'DadosDaRequisicao_DadosContratuais_TipoContrato')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select)
    sleep(1)

    driver.execute_script(f"""
    arguments[0].value = '{valor}';
    arguments[0].dispatchEvent(new Event('change'));
    """, select)

    print("📄 Tipo contrato OK")

# =========================
# 🔢 QTD VAGAS
# =========================
def preencher_qtd_vagas(driver, qtd):
    wait = WebDriverWait(driver, 60)

    print("🔢 Qtd vagas...")

    campo = wait.until(EC.visibility_of_element_located((By.ID,
    'DadosDaRequisicao_DadosContratuais_QuantidadeDeVagasRequisitadas')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
    sleep(1)

    campo.clear()
    sleep(1)
    campo.send_keys(str(qtd))

    print("🔢 Qtd vagas OK")

# =========================
# 🗒️ OBSERVAÇÃO
# =========================
def preencher_observacao(driver, observacao):
    wait = WebDriverWait(driver, 60)

    print("🗒️ Observação...")

    campo = wait.until(EC.visibility_of_element_located((By.ID,
    'DadosDaRequisicao_ObservacaoRequisicao')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
    sleep(1)

    campo.send_keys(str(observacao))

    print("🗒️ Observação OK")

# =========================
# 💰 SALÁRIO
# =========================
def preencher_salario(driver, valor):
    wait = WebDriverWait(driver, 60)

    print("💰 Salário...")

    campo = wait.until(EC.presence_of_element_located((By.ID,
    'DadosDaRequisicao_DadosContratuais_ValorSalario')))

    driver.execute_script(f"arguments[0].value = '{valor}';", campo)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", campo)

    print("💰 Salário OK")


# =========================
# ⏰ ESCALA
# =========================
def preencher_escala(driver, escala):
    wait = WebDriverWait(driver, 60)

    print("⏰ Escala...")

    campo = wait.until(EC.element_to_be_clickable((By.XPATH,
    '//span[@aria-labelledby="select2-DadosDaRequisicao_DadosContratuais_CodigoEscalaEscolhida-container"]')))

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
    sleep(1)

    actions = ActionChains(driver)
    actions.move_to_element(campo).click().perform()

    input_busca = wait.until(EC.visibility_of_element_located((By.XPATH,
    '//span[contains(@class,"select2-dropdown")]//input[contains(@class,"select2-search__field")]')))
    input_busca.send_keys(str(escala))
    sleep(5)

    opcao = wait.until(EC.element_to_be_clickable((By.XPATH,
    '//li[contains(@class,"select2-results__option") and not(contains(@class,"select2-results__option--disabled"))]')))

    actions2 = ActionChains(driver)
    actions2.move_to_element(opcao).click().perform()

    print("⏰ Escala OK")


# =========================
# 📂 CATEGORIA
# =========================
def preencher_categoria(driver, categoria):
    wait = WebDriverWait(driver, 60)

    print("📂 Categoria...")

    mapa = {
        'Estágio/Jovem/Assistencial/Operacional': 9
    }

    valor = mapa.get(str(categoria).strip())

    if not valor:
        raise Exception(f"Categoria inválida: {categoria}")

    select = wait.until(EC.presence_of_element_located((By.ID,
    'DadosDaRequisicao_DadosSLA_Categoria')))

    driver.execute_script("arguments[0].scrollIntoView(true);", select)
    sleep(1)

    driver.execute_script(f"""
    arguments[0].value = '{valor}';
    arguments[0].dispatchEvent(new Event('change'));
    """, select)

    print("📂 Categoria OK")
    print ("Identificando resultado final...")
    sleep(3)

# =========================
# 🔥 RESULTADO FINAL
# =========================
def capturar_resultado_final(driver):
    wait = WebDriverWait(driver, 60)

    try:
        elemento = wait.until(EC.presence_of_element_located((By.XPATH,
        '/html/body/div[12]/p/h3')))

        texto = elemento.text
        print(f"🎯 RQ criada: {texto}")

        return True, texto

    except:
        try:
            erro = wait.until(EC.presence_of_element_located((By.XPATH,
            '/html/body/div[2]/form/div/div[4]/dl/dd/div')))

            erro_texto = erro.text
            print(f"⚠️ Erro LG: {erro_texto}")

            return False, erro_texto

        except:
            return False, "SEM RETORNO"

# =========================
# 🚀 EXECUÇÃO
# =========================
def executar(driver, callback=None, pasta=r"Z:\PROCESSOS\Importacao", usuario=None, senha=None):
    wait = WebDriverWait(driver, 60)

    df, caminho = carregar_excel(pasta)
    total = len(df)

    # ================================
    # 🔄 RE-LOGIN APÓS SESSÃO EXPIRADA
    # ================================
    def reconectar(tentativa=1):
        MAX_TENTATIVAS = 3
        if tentativa > MAX_TENTATIVAS:
            raise Exception(f"Re-login falhou após {MAX_TENTATIVAS} tentativas consecutivas.")

        if callback:
            callback(f"🔄 Sessão expirada — re-login (tentativa {tentativa}/{MAX_TENTATIVAS})...")

        print(f"🔄 Re-login tentativa {tentativa}...")

        from core.login import fazer_login
        try:
            fazer_login(driver, usuario, senha, "abrir")
            abrir_abertura_vagas(driver)
            print("✅ Re-login OK, voltando ao ponto onde parou.")
            if callback:
                callback("✅ Re-login OK, retomando processo...")
        except Exception as e:
            print(f"⚠️ Falha no re-login: {e} — tentando novamente...")
            sleep(10)
            reconectar(tentativa + 1)

    abrir_abertura_vagas(driver)

    for i in range(total):
        progresso = int(((i + 1) / total) * 100)

        try:
            print(f"\n[{i+1}/{total}] 🔄 Processando...")
            if callback:
                callback(f"[{i+1}/{total}] 🔄 Processando...", progresso)

            etapa_atual = "INICIO"

            # ✅ Leitura antecipada para uso em todo o loop
            motivo_requisicao = df.iloc[i, 1]
            qtd_vagas = df.iloc[i, 6]

            # 🔥 GESTOR
            etapa_atual = "GESTOR"
            if callback:
                callback(f"[{i+1}/{total}] 👤 Selecionando gestor...", progresso)
            wait_for_page_load(driver)
            selecionar_gestor(driver, df.iloc[i, 0])
            sleep(3)

            # 🔥 MOTIVO
            etapa_atual = "MOTIVO"
            if callback:
                callback(f"[{i+1}/{total}] 📌 Selecionando motivo...", progresso)
            wait_for_page_load(driver)
            selecionar_motivo(driver, motivo_requisicao)
            sleep(3)

            # 🔥 EMPRESA
            etapa_atual = "EMPRESA"
            if callback:
                callback(f"[{i+1}/{total}] 🏢 Preenchendo empresa...", progresso)
            wait_for_page_load(driver)
            preencher_empresa(driver, df.iloc[i, 2], motivo_requisicao)
            sleep(3)

            # 🔥 POSIÇÃO
            etapa_atual = "POSICAO"
            if callback:
                callback(f"[{i+1}/{total}] 📌 Preenchendo posição...", progresso)
            wait_for_page_load(driver)
            preencher_posicao(driver, df.iloc[i, 3], motivo_requisicao)
            sleep(5)

            # 🔥 SUBSTITUTO — apenas se o motivo contiver "Substituição"
            if any(m in str(motivo_requisicao) for m in MOTIVOS_SUBSTITUICAO_DESLIGAMENTO) or "Movimentações" in str(motivo_requisicao):
                etapa_atual = "SUBSTITUTO"
                if callback:
                   callback(f"[{i+1}/{total}] 👤 Preenchendo substituto...", progresso)
                preencher_substituto(driver, df.iloc[i, 4], motivo_requisicao, df.iloc[i, 5])
                sleep(3)

            # 🔥 DESCRIÇÃO
            etapa_atual = "DESCRICAO"
            if callback:
                callback(f"[{i+1}/{total}] 📝 Preenchendo descrição...", progresso)
            preencher_descricao(driver, df.iloc[i, 7])
            sleep(3)

            #tipo_contrato = df.iloc[i, 8]
            etapa_atual = "TIPO_CONTRATO"
            if callback:
                callback(f"[{i+1}/{total}] 📄 Preenchendo tipo contrato...", progresso)
            preencher_tipo_contrato(driver, df.iloc[i, 8])
            sleep(3)

            # 🔥 QTD VAGAS — apenas se não for Substituição
            if "Substituição" not in str(motivo_requisicao):
                etapa_atual = "QTD_VAGAS"
                if callback:
                    callback(f"[{i+1}/{total}] 🔢 Preenchendo qtd vagas...", progresso)
                preencher_qtd_vagas(driver, qtd_vagas)
                sleep(3)

            # 🔥 OBS
            etapa_atual = "OBS"
            if callback:
                callback(f"[{i+1}/{total}] 🗒️ Preenchendo observação...", progresso)
            preencher_observacao(driver, df.iloc[i, 10] if len(df.columns) > 9 else "TESTE")
            sleep(3)

            # 🔥 SALÁRIO
            etapa_atual = "SALARIO"
            if callback:
                callback(f"[{i+1}/{total}] 💰 Preenchendo salário...", progresso)
            preencher_salario(driver, df.iloc[i, 11])
            sleep(3)

            # 🔥 ESCALA
            etapa_atual = "ESCALA"
            if callback:
                callback(f"[{i+1}/{total}] ⏰ Preenchendo escala...", progresso)
            preencher_escala(driver, df.iloc[i, 12])
            sleep(3)

            # 🔥 CATEGORIA
            etapa_atual = "CATEGORIA"
            if callback:
                callback(f"[{i+1}/{total}] 📂 Preenchendo categoria...", progresso)
            preencher_categoria(driver, df.iloc[i, 13])
            sleep(3)

            # 🔥 FINALIZAR
            etapa_atual = "BOTAO_FINAL"
            if callback:
                callback(f"[{i+1}/{total}] 🚀 Finalizando vaga...", progresso)
            btn = wait.until(EC.element_to_be_clickable((By.XPATH,
            '/html/body/div[2]/form/div/div[10]/div/div/div/button[2]')))
            btn.click()

            print("Identificando resultado final...")
            if callback:
                callback(f"[{i+1}/{total}] ⏳ Aguardando resultado...", progresso)
            sleep(25)

            sucesso, retorno = capturar_resultado_final(driver)

            if sucesso:
                print(f"[{i+1}/{total}] ✅ SUCESSO")
                if callback:
                    callback(f"[{i+1}/{total}] ✅ Sucesso → {retorno}", progresso)
                df.at[i, 'STATUS'] = 'OK'
                df.at[i, 'NUMERO_RQ'] = retorno
            else:
                print(f"[{i+1}/{total}] ❌ ERRO NEGÓCIO")
                if callback:
                    callback(f"[{i+1}/{total}] ❌ Erro negócio → {retorno}", progresso)
                df.at[i, 'STATUS'] = 'ERRO'
                df.at[i, 'NUMERO_RQ'] = retorno

            df.to_excel(caminho, index=False)

            sleep(40)
            driver.refresh()
            sleep(5)
            try:
                reentrar_iframe(driver)
            except SessaoExpiradaError:
                reconectar()

        except SessaoExpiradaError:
            print(f"[{i+1}/{total}] 🔄 Sessão expirou em {etapa_atual} — re-login e retry")
            if callback:
                callback(f"[{i+1}/{total}] 🔄 Sessão expirou ({etapa_atual}) — re-login...", progresso)

            df.at[i, 'STATUS'] = 'ERRO'
            df.at[i, 'NUMERO_RQ'] = f'SESSAO_EXPIRADA - {etapa_atual}'
            df.to_excel(caminho, index=False)

            reconectar()

        except Exception as e:
            print(f"[{i+1}/{total}] ❌ ERRO")
            print(e)
            if callback:
                callback(f"[{i+1}/{total}] ❌ ERRO - {etapa_atual}: {e}", progresso)

            df.at[i, 'STATUS'] = 'ERRO'
            df.at[i, 'NUMERO_RQ'] = f'ERRO - {etapa_atual}'

            df.to_excel(caminho, index=False)

            driver.refresh()
            sleep(5)
            try:
                reentrar_iframe(driver)
            except SessaoExpiradaError:
                reconectar()

    print("\n🚀 FINALIZADO")
    if callback:
        callback("✅ Finalizado", 100)
