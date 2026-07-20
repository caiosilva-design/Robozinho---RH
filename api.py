from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
import threading
import time
from datetime import datetime

from runner import executar_processo

app = FastAPI()

status_global = {
    "status": "idle",
    "log": [],
    "progresso": 0
}


class ExecucaoRequest(BaseModel):
    tipo: str
    usuario: str
    senha: str = Field(exclude=True)
    horario_inicio: Optional[str] = None  # formato ISO: "2024-05-10T08:30:00"
    pasta: Optional[str] = r"Z:\PROCESSOS\Importacao"


def callback(msg, progresso=None):
    status_global["status"] = msg
    status_global["log"].append(msg)
    if progresso is not None:
        status_global["progresso"] = progresso


def rodar(tipo, usuario, senha, horario_inicio: Optional[datetime], pasta: str):
    if horario_inicio:
        agora = datetime.now()
        espera = (horario_inicio - agora).total_seconds()

        if espera > 0:
            callback(f"⏳ Aguardando até {horario_inicio.strftime('%d/%m/%Y %H:%M')}...")

            # Aguarda em blocos de 10s para poder logar o tempo restante
            while True:
                agora = datetime.now()
                restante = (horario_inicio - agora).total_seconds()
                if restante <= 0:
                    break

                if restante > 60:
                    mins = int(restante // 60)
                    callback(f"⏳ Faltam {mins} min para execução...")
                    time.sleep(min(60, restante))
                else:
                    callback(f"⏳ Faltam {int(restante)}s para execução...")
                    time.sleep(min(10, restante))

    callback("🚀 Iniciando execução...")
    executar_processo(tipo, callback, usuario, senha, pasta)
    senha = None


@app.post("/executar")
def executar(req: ExecucaoRequest):
    status_global["status"] = "iniciando"
    status_global["log"] = []
    status_global["progresso"] = 0

    horario_inicio = None
    if req.horario_inicio:
        try:
            horario_inicio = datetime.fromisoformat(req.horario_inicio)
        except ValueError:
            return {"erro": "Formato de horario_inicio inválido. Use ISO 8601: YYYY-MM-DDTHH:MM:SS"}

    thread = threading.Thread(
        target=rodar,
        args=(req.tipo, req.usuario, req.senha, horario_inicio, req.pasta),
        daemon=True
    )
    thread.start()

    return {"msg": "Processo recebido", "agendado": req.horario_inicio or "imediato"}


@app.get("/status")
def status():
    return status_global

#if __name__ == "__main__":
    #import uvicorn
    #uvicorn.run("api:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import uvicorn
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile=os.path.join(BASE_DIR, "key.pem"),
        ssl_certfile=os.path.join(BASE_DIR, "cert.pem")
    )
