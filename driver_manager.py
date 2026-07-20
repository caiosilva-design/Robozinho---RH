import requests
import zipfile
import urllib3
import winreg
from pathlib import Path
import shutil
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 📂 pasta fixa (recomendado servidor)
def get_base_path():
    base = Path("C:/robo_rh/driver")
    base.mkdir(parents=True, exist_ok=True)
    return base


# 🔎 Detecta versão do Chrome
def get_chrome_version():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Google\Chrome\BLBeacon"
        )
        version, _ = winreg.QueryValueEx(key, "version")
        return version
    except:
        return None


# 🌐 API moderna
def get_modern_driver_url(chrome_version):
    try:
        url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(url, verify=False, timeout=30)
        data = response.json()

        major_version = chrome_version.split(".")[0]

        for v in data["versions"]:
            if v["version"].startswith(major_version):
                for item in v["downloads"]["chromedriver"]:
                    if item["platform"] == "win64":
                        return item["url"]
    except:
        pass

    return None


# 🧓 fallback
def get_legacy_driver_url(chrome_version):
    try:
        major = chrome_version.split(".")[0]
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major}"

        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None

        driver_version = response.text.strip()

        return f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
    except:
        return None


# 💾 DOWNLOAD + EXTRAÇÃO (CORRIGIDO)
def download_and_extract(url, base_path):
    zip_path = base_path / "chromedriver.zip"

    print("⬇️ Baixando ChromeDriver...")
    r = requests.get(url, stream=True, verify=False)

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

    print("📦 Tamanho do ZIP:", zip_path.stat().st_size, "bytes")

    print("📦 Extraindo...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(base_path)

    print("📂 LISTANDO TUDO QUE FOI EXTRAÍDO:")

    for root, dirs, files in os.walk(base_path):
        for name in files:
            print("👉", os.path.join(root, name))

    zip_path.unlink(missing_ok=True)

    # 🔍 procurar chromedriver
    for root, dirs, files in os.walk(base_path):
        for name in files:
            if "chromedriver" in name.lower():
                origem = os.path.join(root, name)
                destino = base_path / "chromedriver.exe"

                shutil.move(origem, destino)

                print("✅ ACHOU:", origem)
                print("🚀 MOVIDO PARA:", destino)

                return destino

    raise Exception("❌ chromedriver.exe não encontrado após extração")


# 🚀 FUNÇÃO PRINCIPAL
def garantir_chromedriver():
    base_path = get_base_path()
    driver_path = base_path / "chromedriver.exe"

    # ✅ já existe
    if driver_path.exists():
        print("✅ Chromedriver já existe")
        return driver_path

    # 🔎 versão do Chrome
    chrome_version = get_chrome_version()

    if not chrome_version:
        raise Exception("❌ Não foi possível detectar a versão do Chrome.")

    print("🌐 Versão do Chrome:", chrome_version)

    # tenta moderna
    url = get_modern_driver_url(chrome_version)

    # fallback
    if not url:
        print("⚠️ Tentando versão legada...")
        url = get_legacy_driver_url(chrome_version)

    if not url:
        raise Exception("❌ Não foi encontrada uma versão compatível.")

    print("🔗 URL encontrada:", url)

    return download_and_extract(url, base_path)
