from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep
import pandas as pd
import os

from core.navegacao import abrir_processo_seletivo, esperar_loading


def ler_excel(pasta=None):
    if pasta:
        caminho = pasta + r"\VAGAS_PARA_CANCELAR.xlsx"

    df = pd.read_excel(caminho)

    if 'STATUS' not in df.columns:
        df['STATUS'] = ''

    df['STATUS'] = df['STATUS'].astype(str)

    return df, caminho


def executar(driver, callback=None, pasta=None):
    wait = WebDriverWait(driver, 30)

    df, caminho = ler_excel(pasta)
    total = len(df)

    print(f"\n🚀 Iniciando processamento de {total} registros...\n")

    # 🔥 PRIMEIRA ENTRADA NA TELA
    sleep(10)
    abrir_processo_seletivo(driver)

    if callback:
        callback(f"🚀 Iniciando processamento de {total} registros...", 0)

    # =========================
    # 🔁 LOOP PRINCIPAL
    # =========================
    for i in range(total):
        progresso = int(((i + 1) / total) * 100)

        if callback:
            callback(f"[{i+1}/{total}] 🔄 Processando...", progresso)

        codigo = df.iloc[i, 0]
        observacao = df.iloc[i, 1] if len(df.columns) > 1 else "Cancelado automaticamente"

        tentativa = 0
        sucesso = False

        while tentativa < 2 and not sucesso:
            try:
                print(f"[{i+1}/{total}] 🔄 Tentativa {tentativa+1} → {codigo}")
                if callback:
                    callback(f"[{i+1}/{total}] 🔄 Tentativa {tentativa+1} → {codigo}", progresso)

                # =========================
                # 🔽 FILTRO
                # =========================
                btn_filtro = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[1]/div/table/tbody/tr/th[13]/div/span'
                    ))
                )
                btn_filtro.click()

                sleep(2)

                campo = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[4]/div/input[1]'
                    ))
                )

                campo.clear()
                campo.send_keys(str(codigo))
                campo.send_keys(Keys.ENTER)

                sleep(4)

                # =========================
                # 🔽 STATUS
                # =========================
                if callback:
                    callback(f"[{i+1}/{total}] 🔄 Alterando status → {codigo}", progresso)

                mudanca = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[2]/table/tbody/tr[1]/td[10]/div[2]/div/div/a/small'
                    ))
                )
                mudanca.click()

                sleep(3)

                cancelado = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[2]/table/tbody/tr[1]/td[10]/div[2]/div/ul/li[4]/a/small'
                    ))
                )
                cancelado.click()

                sleep(3)

                # =========================
                # 🔽 OBSERVAÇÃO
                # =========================
                if callback:
                    callback(f"[{i+1}/{total}] 🗒️ Preenchendo observação → {codigo}", progresso)

                btn_obs = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[2]/table/tbody/tr[1]/td[9]/img'
                    ))
                )
                btn_obs.click()

                sleep(3)

                campo_obs = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[2]/div/div[1]/div/textarea'
                    ))
                )

                campo_obs.clear()
                campo_obs.send_keys(str(observacao))

                sleep(2)

                botao_salvar = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[3]/div[2]/div/div[7]/div[2]/div[2]/div/div[2]/div/input[2]'
                    ))
                )
                botao_salvar.click()

                # ✅ SUCESSO
                df.at[i, 'STATUS'] = 'CANCELADO'
                df.to_excel(caminho, index=False)

                print(f"[{i+1}/{total}] ✅ Cancelado\n")
                if callback:
                    callback(f"[{i+1}/{total}] ✅ Cancelado → {codigo}", progresso)

                sucesso = True
                sleep(2)

            except Exception as e:
                tentativa += 1
                print(f"[{i+1}/{total}] ⚠️ Erro tentativa {tentativa} → {codigo}")
                if callback:
                    callback(f"[{i+1}/{total}] ⚠️ Erro tentativa {tentativa} → {codigo}", progresso)

                if tentativa < 2:
                    print("🔄 Recarregando página...")
                    if callback:
                        callback(f"[{i+1}/{total}] 🔄 Recarregando página...", progresso)

                    driver.refresh()

                    # 🔥 ESPERA INTELIGENTE
                    esperar_loading(driver)
                    sleep(5)

                    print("🔁 Voltando para Processo Seletivo...")
                    abrir_processo_seletivo(driver)
                    sleep(5)

                else:
                    print(f"[{i+1}/{total}] ❌ Falha definitiva → {codigo}")
                    if callback:
                        callback(f"[{i+1}/{total}] ❌ Falha definitiva → {codigo}", progresso)

                    df.at[i, 'STATUS'] = 'ERRO'
                    df.to_excel(caminho, index=False)

    print("🚀 PROCESSO FINALIZADO")
    if callback:
        callback("✅ Finalizado", 100)
