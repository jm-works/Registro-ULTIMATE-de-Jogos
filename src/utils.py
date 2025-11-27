import re
from datetime import datetime


def centralizar_janela(janela, largura, altura):
    """Centraliza uma janela do Tkinter na tela."""
    janela.update_idletasks()
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela - largura) // 2
    y = (altura_tela - altura) // 2
    janela.geometry(f"{largura}x{altura}+{x}+{y}")


def validar_campos(
    titulo, genero, plataforma, data_zeramento, tempo_jogado, nota, estado
):
    """Verifica se os dados inseridos no formulário são válidos."""
    if not titulo.strip():
        return "O campo 'Título' é obrigatório! Não deixe seu jogo sem nome."
    if not genero.strip():
        return "O campo 'Gênero' é obrigatório! Escolha o tipo do seu jogo."
    if not plataforma.strip():
        return "O campo 'Plataforma' é obrigatório! Onde você jogou?"
    if not estado.strip():
        return "O campo 'Forma de Zeramento' é obrigatório!"

    # Se não for apenas planejado/desistência, exige dados de conclusão
    if estado not in ["Planejo Jogar", "Desistência"]:
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", data_zeramento):
            return "A data de zeramento deve estar no formato DIA/MÊS/ANO."
        try:
            datetime.strptime(data_zeramento, "%d/%m/%Y")
        except ValueError:
            return "A data de zeramento não é válida!"

        if not re.match(r"^\d+:\d{2}$", tempo_jogado):
            return "O tempo jogado deve estar no formato HORAS:MINUTOS!"
        try:
            horas, minutos = map(int, tempo_jogado.split(":"))
            if horas < 0 or minutos < 0 or minutos >= 60:
                return "Minutos inválidos (0-59)."
        except ValueError:
            return "O tempo jogado é inválido!"

    if nota:
        try:
            n = float(nota)
            if not (1 <= n <= 10):
                return "A nota deve estar entre 1 e 10!"
        except ValueError:
            pass

    return None


def calcular_total_minutos(tempo_jogado):
    """Converte 'HH:MM' para total de minutos (int)."""
    if not tempo_jogado or ":" not in tempo_jogado:
        return 0
    try:
        horas, minutos = map(int, tempo_jogado.split(":"))
        return horas * 60 + minutos
    except ValueError:
        return 0
