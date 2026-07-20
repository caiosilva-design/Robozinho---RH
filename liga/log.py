import os
from datetime import datetime

def salvar_log(resumo):

    pasta = "logs"
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
    caminho = os.path.join(pasta, nome_arquivo)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(resumo)

    return caminho
