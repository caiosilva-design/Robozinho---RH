from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from config.settings import URL_LOGIN, URL_LOGIN2 #,LOGIN, SENHA,


def fazer_login(driver, usuario, senha, tipo="cancelar"):

    # 🔥 escolhe URL
    if tipo == "abrir":
        url = URL_LOGIN2
    else:
        url = URL_LOGIN

    driver.get(url)

    wait = WebDriverWait(driver, 30)

    campo_login = wait.until(
        EC.presence_of_element_located((By.ID, "Login"))
    )
    campo_login.send_keys(usuario)
    campo_login.send_keys(Keys.ENTER)

    campo_senha = wait.until(
        EC.presence_of_element_located((By.ID, "Senha"))
    )
    campo_senha.send_keys(senha)
    campo_senha.send_keys(Keys.ENTER)

    wait.until(lambda d: "SuiteGente" in d.current_url or "hapvida" in d.current_url)

    print(f"Login concluído com sucesso! ({tipo})")
