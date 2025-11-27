import json
import os
import re
from datetime import datetime
from src.constantes import SAVES_DIR


class GerenciadorDados:
    def __init__(self):
        self.arquivo_jogos = os.path.join(SAVES_DIR, "jogos.json")
        self.arquivo_tarefas = os.path.join(SAVES_DIR, "tarefas.json")

        os.makedirs(SAVES_DIR, exist_ok=True)

    def carregar_jogos(self):
        """Carrega a lista de jogos, ordenando por data os que já foram zerados."""
        try:
            with open(self.arquivo_jogos, "r", encoding="utf-8") as arquivo:
                lista_jogos = json.load(arquivo)

            jogos_com_data = [
                jogo
                for jogo in lista_jogos
                if jogo.get("Data de Zeramento")
                and re.match(r"^\d{2}/\d{2}/\d{4}$", jogo["Data de Zeramento"])
            ]
            jogos_sem_data = [
                jogo
                for jogo in lista_jogos
                if not jogo.get("Data de Zeramento")
                or not re.match(r"^\d{2}/\d{2}/\d{4}$", jogo["Data de Zeramento"])
            ]

            jogos_com_data.sort(
                key=lambda jogo: datetime.strptime(
                    jogo["Data de Zeramento"], "%d/%m/%Y"
                )
            )

            return jogos_com_data + jogos_sem_data

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_jogos(self, lista_jogos):
        try:
            with open(self.arquivo_jogos, "w", encoding="utf-8") as arquivo:
                json.dump(lista_jogos, arquivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar jogos: {e}")
            return False

    def carregar_tarefas(self):
        try:
            with open(self.arquivo_tarefas, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_tarefas(self, tarefas):
        try:
            with open(self.arquivo_tarefas, "w", encoding="utf-8") as arquivo:
                json.dump(tarefas, arquivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar tarefas: {e}")
            return False

    def resetar_tudo(self):
        if os.path.exists(self.arquivo_jogos):
            os.remove(self.arquivo_jogos)
        if os.path.exists(self.arquivo_tarefas):
            os.remove(self.arquivo_tarefas)
