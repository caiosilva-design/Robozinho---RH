from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def iniciar_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")

        try:
            # 🔥 tenta usar chromedriver do PATH primeiro
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chromedriver do PATH")
            return driver

        except Exception:
            # 🔥 fallback: baixa via driver_manager
            print("⚠️ Chromedriver não encontrado no PATH, baixando...")
            from driver_manager import garantir_chromedriver
            caminho_driver = garantir_chromedriver()
            service = Service(str(caminho_driver))
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chromedriver do driver_manager")
            return driver

    except Exception as e:
        print("❌ Erro ao iniciar o navegador:", e)
        raise

