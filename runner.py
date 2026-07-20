import os
import traceback
from datetime import datetime
import threading

from core.driver import iniciar_driver
from core.login import fazer_login
from processos.abrir_vagas import executar as abrir
from processos.cancelar_vagas import executar as cancelar

from utils import enviar_email
from logs.log import salvar_log


# =========================
# 🚀 EXECUÇÃO PRINCIPAL
# =========================
def executar_processo(tipo, callback, usuario, senha, pasta=r"Z:\PROCESSOS\Importacao"):

    logs_execucao = []
    def log(msg, progresso=None):
        print(msg)  # continua aparecendo no VS Code
        logs_execucao.append(msg)
        
        # callback em thread separada para não bloquear o Selenium
        def _cb():
            try:
                if callback:
                    callback(msg, progresso)
            except Exception as e:
                print("⚠️ Erro no callback:", e)
        threading.Thread(target=_cb, daemon=True).start()
              
    inicio = datetime.now()
    caminho_excel = None

    log(f"🟢 Início: {inicio.strftime('%H:%M:%S')}")
    log("🔄 Inicializando navegador...")

    driver = iniciar_driver()

    try:
        if tipo == "abrir":
            log("🔐 Fazendo login...")
            fazer_login(driver, usuario, senha, "abrir")

            log("🚀 Executando abertura...")
            abrir(driver, log, pasta)

            caminho_excel = os.path.join(
                os.path.expanduser("~"),
                "Downloads",
                "VAGAS_PARA_ABERTURA.xlsx"
            )

        elif tipo == "cancelar":
            log("🔐 Fazendo login...")
            fazer_login(driver, usuario, senha, "cancelar")

            log("🚀 Executando cancelamento...")
            cancelar(driver, log, pasta)

            caminho_excel = os.path.join(
                os.path.expanduser("~"),
                "Downloads",
                "VAGAS_PARA_CANCELAR.xlsx"
            )

        else:
            log("❌ Processo inválido")
            return

    except Exception as e:
        log(f"❌ Erro geral: {str(e)}")
        log(f"📋 Traceback: {traceback.format_exc()}")

    finally:
        fim = datetime.now()
        duracao = fim - inicio

        # 🔥 formata tempo bonito
        tempo_total = str(duracao).split(".")[0]

        log(f"🔴 Fim: {fim.strftime('%H:%M:%S')}")
        log(f"⏱️ Tempo total: {tempo_total}")

        resumo = f"""
Robô RH - Execução finalizada

🟢 Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}
🔴 Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}
⏱️ Tempo total: {tempo_total}

📋 LOG COMPLETO:
""" + "\n".join(logs_execucao)

        # 🧾 salva log
        salvar_log(resumo)

        # 📧 envia email
        try:
            enviar_email(resumo, caminho_excel)
            callback("📧 Email enviado!")
        except Exception as e:
            callback(f"Erro email: {e}")

        callback("✅ Finalizado!")


# =========================
# 🧵 THREAD (ESSENCIAL)
# =========================
def iniciar_thread(tipo, callback, usuario, senha):
    thread = threading.Thread(
        target=executar_processo,
        args=(tipo, callback, usuario, senha),
        daemon=True
    )
    thread.start()
