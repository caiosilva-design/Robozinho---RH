from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

# =========================
# 🔴 EXCEÇÃO DE SESSÃO
# =========================
class SessaoExpiradaError(Exception):
    """Levantada quando o LG caiu/atualizou e o iframe sumiu."""
    pass


# =========================
# ⏳ LOADING
# =========================

def esperar_loading(driver):
    wait = WebDriverWait(driver, 30)
    try:
        wait.until(
            EC.invisibility_of_element_located((
                By.XPATH,
                "//div[contains(@class,'blockUI')]"
            ))
        )
    except:
        pass


# =========================
# ❌ CANCELAR VAGAS
# =========================

def abrir_processo_seletivo(driver):
    wait = WebDriverWait(driver, 30)

    driver.switch_to.default_content()

    print("Aguardando tela estabilizar...")
    esperar_loading(driver)

    print("Abrindo menu...")

    btn_menu = wait.until(
        EC.presence_of_element_located((By.ID, "btnMenuBarraSidebar"))
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", btn_menu)
    sleep(1)
    driver.execute_script("arguments[0].click();", btn_menu)

    sleep(2)
    esperar_loading(driver)

    print("Indo para Recrutamento e Seleção...")

    btn_recrutamento = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            '/html/body/div[3]/div/div[2]/div/div[2]/div/div[11]'
        ))
    )

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_recrutamento)
    sleep(1)
    driver.execute_script("arguments[0].click();", btn_recrutamento)

    sleep(4)
    esperar_loading(driver)

    print("Entrando no iframe...")

    iframe = wait.until(
        EC.presence_of_element_located((By.ID, "moduloIframe"))
    )
    driver.switch_to.frame(iframe)

    print("Clicando em Processo Seletivo...")

    btn_processo = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            '/html/body/div[4]/div/div/div[3]/div[2]/div/div[2]/div/div[2]/ul/li[4]/span[1]'
        ))
    )

    driver.execute_script("arguments[0].click();", btn_processo)

    sleep(4)
    esperar_loading(driver)

    print("Tela Processo Seletivo pronta ✅")


# =========================
# ✅ ABRIR VAGAS
# =========================

def abrir_abertura_vagas(driver):
    wait = WebDriverWait(driver, 60)

    driver.switch_to.default_content()
    esperar_loading(driver)

    print("\n📂 MENU LG")

    # =========================
    # MENU LATERAL
    # =========================
    print("➡️ Abrindo menu lateral")

    btn_lateral = wait.until(
        EC.presence_of_element_located((By.XPATH,
        '/html/body/div[1]/div/div/header/a'))
    )
    btn_lateral.click()

    sleep(3)

    # =========================
    # SOLICITAÇÕES
    # =========================
    print("➡️ Solicitações")

    btn_solicitacoes = wait.until(
        EC.presence_of_element_located((By.XPATH,
        '/html/body/div[2]/div/div[2]/div/div[1]/div/div[1]/ul/li[3]/a'))
    )
    btn_solicitacoes.click()

    sleep(3)

    # =========================
    # GESTOR
    # =========================
    print("➡️ Gestor")

    btn_gestor = wait.until(
        EC.presence_of_element_located((By.XPATH,
        '/html/body/div[2]/div/div[2]/div/div[1]/div/div[1]/ul/li[3]/ul/li[4]/a'))
    )
    btn_gestor.click()

    sleep(2)

    # =========================
    # REQUISIÇÃO
    # =========================
    print("➡️ Requisição")

    btn_requisicao = wait.until(
        EC.presence_of_element_located((By.XPATH,
        '/html/body/div[2]/div/div[2]/div/div[1]/div/div[1]/ul/li[3]/ul/li[4]/ul/li[4]'))
    )
    btn_requisicao.click()

    # =========================
    # 🔥 CARGA PESADA LG (IGUAL ORIGINAL)
    # =========================
    print("⏳ Aguardando carga pesada LG...")
    sleep(10)

    # =========================
    # 🔥 IFRAME
    # =========================
    print("🔎 Entrando no iframe (modo antigo)...")

    div = driver.find_element('xpath', '/html/body')
    div1 = div.find_element('xpath', '/html/body/div[1]')
    div2 = div1.find_element('xpath', '/html/body/div[1]/div')
    div3 = div2.find_element('xpath', '/html/body/div[1]/div/section')
    div4 = div.find_element('xpath', '/html/body/div[1]/div/section/section')
    div5 = div4.find_element('xpath', '/html/body/div[1]/div/section/section/div[1]')
    iframe = div5.find_element('xpath', '/html/body/div[1]/div/section/section/div[1]/iframe')

    driver.switch_to.frame(iframe)

    print("✅ Iframe REAL acessado")

    sleep(1)

    # 🔥 GARANTE QUE NÃO TEM OVERLAY
    esperar_loading(driver)
    sleep(1)

    # =========================
    # RETORNAR NA ATUALIZAÇÃO
    # =========================

def reentrar_iframe(driver):
    wait = WebDriverWait(driver, 60)

    driver.switch_to.default_content()

    print("⏳ Aguardando carga pesada LG...")
    sleep(10)

    print("🔎 Reentrando direto no iframe...")

    div = driver.find_element('xpath', '/html/body')
    div1 = div.find_element('xpath', '/html/body/div[1]')
    div2 = div1.find_element('xpath', '/html/body/div[1]/div')
    div3 = div2.find_element('xpath', '/html/body/div[1]/div/section')
    div4 = div.find_element('xpath', '/html/body/div[1]/div/section/section')
    div5 = div4.find_element('xpath', '/html/body/div[1]/div/section/section/div[1]')
    iframe = div5.find_element('xpath', '/html/body/div[1]/div/section/section/div[1]/iframe')

    driver.switch_to.frame(iframe)

    print("✅ Iframe reanexado")

    sleep(1)

    esperar_loading(driver)
    sleep(1)    
