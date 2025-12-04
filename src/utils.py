import re
import tkinter as tk
from datetime import datetime
from typing import Optional, Union
from src.constantes import GENEROS


def centralizar_janela(
    janela: Union[tk.Tk, tk.Toplevel], largura: int, altura: int
) -> None:
    janela.update_idletasks()
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela - largura) // 2
    y = (altura_tela - altura) // 2
    janela.geometry(f"{largura}x{altura}+{x}+{y}")


def validar_campos(
    titulo: str,
    genero: str,
    plataforma: str,
    data_zeramento: str,
    tempo_jogado: str,
    nota: Union[str, float, int],
    estado: str,
) -> Optional[str]:
    if not titulo.strip():
        return "O campo 'Título' é obrigatório! Não deixe seu jogo sem nome."
    if not genero.strip():
        return "O campo 'Gênero' é obrigatório! Escolha o tipo do seu jogo."
    if genero not in GENEROS:
        return "Gênero inválido! Por favor, utilize a lupa para selecionar um gênero da lista oficial."
    if not plataforma.strip():
        return "O campo 'Plataforma' é obrigatório! Onde você jogou?"
    if not estado.strip():
        return "O campo 'Forma de Zeramento' é obrigatório!"
    if estado not in ["Planejo Jogar", "Desistência"]:
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", data_zeramento):
            return "A data de zeramento deve estar no formato DIA/MÊS/ANO."
        try:
            datetime.strptime(data_zeramento, "%d/%m/%Y")
        except ValueError:
            return "A data de zeramento não é válida!"

        tempo_limpo = tempo_jogado.replace(" ", "").lower()
        if not re.match(r"^(\d+h\d{2}m)$", tempo_limpo):
            return "O tempo jogado está com formato inválido (ex: 10h 30m)."

    if nota:
        try:
            n = float(nota)
            if not (1 <= n <= 10):
                return "A nota deve estar entre 1 e 10!"
        except ValueError:
            pass

    return None


def calcular_total_minutos(tempo_jogado: str) -> int:
    if not tempo_jogado:
        return 0
    t = tempo_jogado.lower().replace(" ", "")

    horas = 0
    minutos = 0

    try:
        if "h" in t and "m" in t:
            parts = t.split("h")
            horas = int(parts[0])
            minutos = int(parts[1].replace("m", ""))
        elif "h" in t:
            parts = t.split("h")
            horas = int(parts[0])
            if len(parts) > 1 and parts[1]:
                minutos = int(parts[1].replace("m", ""))
        elif ":" in t:
            parts = t.split(":")
            horas = int(parts[0])
            minutos = int(parts[1])
        elif t.isdigit():
            return int(t) * 60

        return horas * 60 + minutos
    except ValueError:
        return 0
