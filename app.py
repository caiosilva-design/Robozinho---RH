import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
from datetime import datetime
import os
import sys
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
load_dotenv(os.path.join(BASE_DIR, "automacao_rh", ".env"))

# 🔥 ALTERA AQUI
#API_URL = "http://10.177.44.173:8000"
API_URL = "https://10.177.44.173:8443"

# 🔒 Senha de acesso ao app
SENHA_APP = os.getenv("SENHA_APP")

# =========================
# 🔒 TELA DE SENHA
# =========================
def verificar_senha_app():
    senha_digitada = entry_senha_app.get()
    if senha_digitada == SENHA_APP:
        frame_senha.pack_forget()
        frame_principal.pack(fill="both", expand=True)
    else:
        label_erro_senha.config(text="❌ Senha incorreta")
        entry_senha_app.delete(0, tk.END)


# =========================
# 🔄 ATUALIZA STATUS
# =========================
def atualizar_ui(msg, progresso=None):
    def update():
        status_label.config(text=msg)

        if progresso is not None:
            progress['value'] = progresso

        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

        if "Finalizado" in msg:
            btn_abrir.config(state="normal")
            btn_cancelar.config(state="normal")

    root.after(0, update)


# =========================
# 🚀 INICIAR PROCESSO
# =========================
def iniciar(tipo):
    progress['value'] = 0

    usuario = entry_user.get()
    senha = entry_pass.get()

    # Valida horário agendado
    data_str = entry_data.get().strip()
    hora_str = entry_hora.get().strip()

    horario_inicio = None
    if data_str or hora_str:
        try:
            agendado_str = f"{data_str} {hora_str}"
            horario_inicio = datetime.strptime(agendado_str, "%d/%m/%Y %H:%M")
            agora = datetime.now()
            if horario_inicio <= agora:
                messagebox.showwarning(
                    "Horário inválido",
                    "O horário agendado deve ser no futuro."
                )
                return
        except ValueError:
            messagebox.showerror(
                "Formato inválido",
                "Use o formato:\nData: DD/MM/AAAA\nHora: HH:MM"
            )
            return

    if not usuario or not senha:
        status_label.config(text="❌ Preencha usuário e senha")
        return

    btn_abrir.config(state="disabled")
    btn_cancelar.config(state="disabled")

    if horario_inicio:
        status_label.config(
            text=f"⏳ Aguardando {horario_inicio.strftime('%d/%m/%Y %H:%M')}..."
        )
    else:
        status_label.config(text="🚀 Enviando para servidor...")
    root.update()

    payload = {
        "tipo": tipo,
        "usuario": usuario,
        "senha": senha,
        "horario_inicio": horario_inicio.strftime("%Y-%m-%dT%H:%M:%S") if horario_inicio else None,
        "pasta": pasta_var.get()
    }

    try:
        requests.post(f"{API_URL}/executar", json=payload, verify=False)

        # 🔁 começa monitoramento
        threading.Thread(target=monitorar_status, daemon=True).start()

    except Exception as e:
        status_label.config(text=f"❌ Erro ao conectar: {e}")
        btn_abrir.config(state="normal")
        btn_cancelar.config(state="normal")


# =========================
# 📡 MONITORAR STATUS
# =========================
def monitorar_status():
    while True:
        try:
            r = requests.get(f"{API_URL}/status", timeout=5, verify=False).json()

            status = r.get("status", "")
            logs = r.get("log", [])
            progresso = r.get("progresso", 0)

            root.after(0, lambda s=status, l=logs, p=progresso: atualizar_tela(s, l, p))

            if "Finalizado" in status:
                break

            time.sleep(2)

        except Exception as e:
            root.after(0, lambda: status_label.config(text="❌ Erro conexão servidor"))
            break


def atualizar_tela(status, logs, progresso=0):
    status_label.config(text=status)

    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "\n".join(logs))
    log_text.see(tk.END)

    progress['value'] = progresso

    if "Finalizado" in status:
        btn_abrir.config(state="normal")
        btn_cancelar.config(state="normal")


# =========================
# 🎨 UI
# =========================
root = tk.Tk()
root.title("Robô RH")
root.geometry("420x600")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")


# ── FRAME DE SENHA DO APP ──────────────────────
frame_senha = tk.Frame(root, bg="#1e1e1e")
frame_senha.pack(fill="both", expand=True)

tk.Label(
    frame_senha, text="🔒 Robô RH", font=("Arial", 18, "bold"),
    bg="#1e1e1e", fg="white"
).pack(pady=40)

tk.Label(
    frame_senha, text="Digite a senha de acesso:",
    bg="#1e1e1e", fg="#aaaaaa"
).pack()

entry_senha_app = tk.Entry(frame_senha, show="*", width=25, font=("Arial", 12))
entry_senha_app.pack(pady=8)
entry_senha_app.bind("<Return>", lambda e: verificar_senha_app())

label_erro_senha = tk.Label(frame_senha, text="", bg="#1e1e1e", fg="#f44336")
label_erro_senha.pack()

tk.Button(
    frame_senha, text="Entrar", command=verificar_senha_app,
    bg="#4CAF50", fg="white", width=20, font=("Arial", 11)
).pack(pady=10)


# ── FRAME PRINCIPAL ────────────────────────────
frame_principal = tk.Frame(root, bg="#1e1e1e")
# (exibido somente após senha correta)

# título
titulo = tk.Label(
    frame_principal, text="Robô RH", font=("Arial", 16, "bold"),
    bg="#1e1e1e", fg="white"
)
titulo.pack(pady=10)

# credenciais do sistema
tk.Label(frame_principal, text="Usuário", bg="#1e1e1e", fg="white").pack()
entry_user = tk.Entry(frame_principal, width=30)
entry_user.pack(pady=5)

tk.Label(frame_principal, text="Senha", bg="#1e1e1e", fg="white").pack()
entry_pass = tk.Entry(frame_principal, show="*", width=30)
entry_pass.pack(pady=5)

# separador
ttk.Separator(frame_principal, orient="horizontal").pack(fill="x", padx=20, pady=8)

# agendamento
tk.Label(
    frame_principal, text="⏰ Agendamento (opcional)",
    bg="#1e1e1e", fg="#aaaaaa", font=("Arial", 9)
).pack()

frame_horario = tk.Frame(frame_principal, bg="#1e1e1e")
frame_horario.pack(pady=4)

tk.Label(frame_horario, text="Data (DD/MM/AAAA)", bg="#1e1e1e", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=8)
tk.Label(frame_horario, text="Hora (HH:MM)", bg="#1e1e1e", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=8)

entry_data = tk.Entry(frame_horario, width=14)
entry_data.grid(row=1, column=0, padx=8)

entry_hora = tk.Entry(frame_horario, width=10)
entry_hora.grid(row=1, column=1, padx=8)

tk.Label(
    frame_principal,
    text="Se não preenchido, executa imediatamente.",
    bg="#1e1e1e", fg="#666666", font=("Arial", 8)
).pack()

# separador
ttk.Separator(frame_principal, orient="horizontal").pack(fill="x", padx=20, pady=8)

# pasta de importação
tk.Label(
    frame_principal, text="📂 Pasta de Importação",
    bg="#1e1e1e", fg="#aaaaaa", font=("Arial", 9)
).pack()

PASTAS = [
    r"Z:\PROCESSOS\Importacao",
    r"Z:\PROCESSOS\Importacao_vs2",
    r"Z:\PROCESSOS\Importacao_vs3",
]

pasta_var = tk.StringVar(value=PASTAS[0])

pasta_dropdown = ttk.Combobox(
    frame_principal,
    textvariable=pasta_var,
    values=PASTAS,
    state="readonly",
    width=35
)
pasta_dropdown.pack(pady=5)

# separador
ttk.Separator(frame_principal, orient="horizontal").pack(fill="x", padx=20, pady=8)

# botões
btn_abrir = tk.Button(
    frame_principal, text="Abrir Vagas", command=lambda: iniciar("abrir"),
    bg="#4CAF50", fg="white", width=25
)
btn_abrir.pack(pady=5)

btn_cancelar = tk.Button(
    frame_principal, text="Cancelar Vagas", command=lambda: iniciar("cancelar"),
    bg="#f44336", fg="white", width=25
)
btn_cancelar.pack(pady=5)

# barra
progress = ttk.Progressbar(frame_principal, orient="horizontal", length=350, mode="determinate")
progress.pack(pady=15)

# status
status_label = tk.Label(frame_principal, text="Aguardando...", bg="#1e1e1e", fg="white")
status_label.pack(pady=5)

# console/log
log_text = tk.Text(frame_principal, height=10, width=50, bg="#2b2b2b", fg="white")
log_text.pack(pady=10)

root.mainloop()
