import json
import os
import re
import shutil
from datetime import datetime
from src.constantes import SAVES_DIR


class GerenciadorDados:
    def __init__(self):
        self.arquivo_jogos = os.path.join(SAVES_DIR, "jogos.json")
        self.arquivo_tarefas = os.path.join(SAVES_DIR, "tarefas.json")

        os.makedirs(SAVES_DIR, exist_ok=True)

    def _salvar_arquivo_seguro(self, caminho: str, dados: list) -> bool:
        temp_file = f"{caminho}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, indent=4, ensure_ascii=False)
                arquivo.flush()
                os.fsync(arquivo.fileno())

            os.replace(temp_file, caminho)
            return True
        except Exception as e:
            print(f"Erro ao salvar em {caminho}: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def carregar_jogos(self) -> list:
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

    def salvar_jogos(self, lista_jogos: list) -> bool:
        return self._salvar_arquivo_seguro(self.arquivo_jogos, lista_jogos)

    def carregar_tarefas(self) -> list:
        try:
            with open(self.arquivo_tarefas, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_tarefas(self, tarefas: list) -> bool:
        return self._salvar_arquivo_seguro(self.arquivo_tarefas, tarefas)

    def resetar_tudo(self):
        if os.path.exists(self.arquivo_jogos):
            os.remove(self.arquivo_jogos)
        if os.path.exists(self.arquivo_tarefas):
            os.remove(self.arquivo_tarefas)
