import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import re


class GeradorGraficos:
    @staticmethod
    def _configurar_janela():
        mng = plt.get_current_fig_manager()
        try:
            mng.window.state("zoomed")
        except AttributeError:
            try:
                mng.full_screen_toggle()
            except:
                pass

    def criar_distribuicao_plataformas(self, lista_jogos):
        validos = [
            j
            for j in lista_jogos
            if j.get("Forma de Zeramento") not in ["Planejo Jogar", "Desistência"]
        ]
        if not validos:
            return False

        contagem = {}
        for j in validos:
            p = j["Plataforma"]
            contagem[p] = contagem.get(p, 0) + 1

        labels = [f"{p} ({q})" for p, q in contagem.items()]

        plt.figure(figsize=(8, 6))
        self._configurar_janela()
        plt.pie(
            list(contagem.values()), labels=labels, autopct="%1.1f%%", startangle=140
        )
        plt.title("Jogos Zerados por Plataforma")
        plt.axis("equal")
        plt.show()
        return True

    def criar_media_notas_plataformas(self, lista_jogos):
        validos = [
            j
            for j in lista_jogos
            if j.get("Forma de Zeramento") not in ["Planejo Jogar", "Desistência"]
        ]
        if not validos:
            return False

        notas_por_plat = {}
        for j in validos:
            p = j["Plataforma"]
            try:
                n = float(j["Nota"])
                if p not in notas_por_plat:
                    notas_por_plat[p] = []
                notas_por_plat[p].append(n)
            except (ValueError, TypeError):
                continue

        if not notas_por_plat:
            return False

        plataformas = list(notas_por_plat.keys())
        medias = [sum(notas) / len(notas) for notas in notas_por_plat.values()]

        plt.figure(figsize=(10, 6))
        self._configurar_janela()
        plt.bar(plataformas, medias, color="skyblue", edgecolor="black")

        for i, v in enumerate(medias):
            plt.text(i, v + 0.1, f"{v:.2f}", ha="center")

        plt.title("Média de Notas por Plataforma")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        return True

    def criar_tempo_total_plataformas(self, lista_jogos):
        validos = [
            j
            for j in lista_jogos
            if j.get("Forma de Zeramento") not in ["Planejo Jogar", "Desistência"]
        ]
        tempo_por_plat = {}

        for j in validos:
            p = j["Plataforma"]
            t = j.get("Tempo Jogado", "")
            if re.match(r"^\d+:\d{2}$", t):
                h, m = map(int, t.split(":"))
                tempo_total = h * 60 + m
                tempo_por_plat[p] = tempo_por_plat.get(p, 0) + tempo_total

        if not tempo_por_plat:
            return False

        plataformas = list(tempo_por_plat.keys())
        horas = [t // 60 for t in tempo_por_plat.values()]

        plt.figure(figsize=(10, 6))
        self._configurar_janela()
        plt.bar(plataformas, horas, color="lightgreen", edgecolor="black")

        for i, v in enumerate(horas):
            plt.text(i, v + 0.1, f"{v}h", ha="center")

        plt.title("Tempo Total (Horas) por Plataforma")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        return True

    def criar_grafico_jogos_por_ano(self, lista_jogos):
        jogos_por_ano = {}
        for j in lista_jogos:
            try:
                ano = datetime.strptime(j["Data de Zeramento"], "%d/%m/%Y").year
                jogos_por_ano[ano] = jogos_por_ano.get(ano, 0) + 1
            except ValueError:
                continue

        if not jogos_por_ano:
            return False

        anos = sorted(jogos_por_ano.keys())
        qtd = [jogos_por_ano[a] for a in anos]

        plt.figure(figsize=(8, 5))
        self._configurar_janela()
        plt.bar(anos, qtd, color="skyblue")
        plt.title("Jogos Zerados por Ano")
        plt.xlabel("Ano")
        plt.xticks(anos, rotation=45)
        plt.tight_layout()
        plt.show()
        return True

    def criar_grafico_comparativo_generos(self, lista_jogos):
        dados = {}
        zerados = [j for j in lista_jogos if j.get("Data de Zeramento")]

        for j in zerados:
            try:
                ano = datetime.strptime(j["Data de Zeramento"], "%d/%m/%Y").year
                gen = j["Gênero"]
                if ano not in dados:
                    dados[ano] = {}
                dados[ano][gen] = dados[ano].get(gen, 0) + 1
            except ValueError:
                continue

        if not dados:
            return False

        anos = sorted(dados.keys())
        generos = sorted(set(g for d in dados.values() for g in d))

        plt.figure(figsize=(10, 6))
        self._configurar_janela()

        for g in generos:
            valores = [dados.get(a, {}).get(g, 0) for a in anos]
            plt.plot(anos, valores, marker="o", label=g)

        plt.title("Comparação de Gêneros por Ano")
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()
        return True

    def criar_analise_de_notas(self, lista_jogos):
        validos = [
            j
            for j in lista_jogos
            if j.get("Forma de Zeramento") not in ["Planejo Jogar", "Desistência"]
        ]
        notas = []
        for j in validos:
            try:
                notas.append(int(float(j["Nota"])))
            except (ValueError, TypeError):
                pass

        if not notas:
            return False

        contagem = {i: notas.count(i) for i in range(1, 11)}
        media = np.mean(notas)

        plt.figure(figsize=(10, 6))
        self._configurar_janela()
        plt.bar(contagem.keys(), contagem.values(), color="skyblue", edgecolor="black")
        plt.axhline(y=media, color="red", linestyle="--", label=f"Média: {media:.2f}")
        plt.title("Distribuição de Notas")
        plt.xticks(range(1, 11))
        plt.legend()
        plt.show()
        return True

    def criar_grafico_generos(self, lista_jogos):
        validos = [
            j
            for j in lista_jogos
            if j.get("Forma de Zeramento")
            in ["História", "100%", "Platina", "Desistência"]
        ]
        if not validos:
            return False

        contagem = {}
        for j in validos:
            gen = j["Gênero"]
            contagem[gen] = contagem.get(gen, 0) + 1

        labels = [f"{k} ({v})" for k, v in contagem.items()]

        plt.figure(figsize=(8, 8))
        self._configurar_janela()
        plt.pie(
            list(contagem.values()), labels=labels, autopct="%1.1f%%", startangle=140
        )
        plt.title("Distribuição de Gêneros")
        plt.axis("equal")
        plt.show()
        return True
