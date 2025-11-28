import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import re


class GeradorGraficos:
    def __init__(self):
        self.bg_color = "#1e1e1e"
        self.plot_bg = "#2d2d2d"
        self.text_color = "#ecf0f1"
        self.grid_color = "#444444"

        self.colors = [
            "#4a90e2",
            "#2ecc71",
            "#e74c3c",
            "#f1c40f",
            "#9b59b6",
            "#1abc9c",
            "#e67e22",
            "#34495e",
        ]

    def _configurar_estilo(self, titulo, xlabel=None, ylabel=None):
        fig = plt.gcf()
        ax = plt.gca()

        fig.patch.set_facecolor(self.bg_color)
        ax.set_facecolor(self.plot_bg)

        ax.set_title(
            titulo, color=self.text_color, fontsize=16, fontweight="bold", pad=20
        )
        if xlabel:
            ax.set_xlabel(xlabel, color=self.text_color, fontsize=12, labelpad=10)
        if ylabel:
            ax.set_ylabel(ylabel, color=self.text_color, fontsize=12, labelpad=10)

        ax.tick_params(axis="x", colors=self.text_color, labelsize=10)
        ax.tick_params(axis="y", colors=self.text_color, labelsize=10)

        for spine in ax.spines.values():
            spine.set_color(self.grid_color)

        ax.grid(True, color=self.grid_color, linestyle="--", alpha=0.3, zorder=0)

        try:
            mng = plt.get_current_fig_manager()
            window = mng.window
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            size = fig.get_size_inches()
            dpi = fig.get_dpi()
            width = int(size[0] * dpi)
            height = int(size[1] * dpi)
            x = int((screen_width / 2) - (width / 2))
            y = int((screen_height / 2) - (height / 2))
            window.geometry(f"{width}x{height}+{x}+{y}")
        except:
            pass

        plt.tight_layout()

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

        sorted_items = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        labels = [f"{p} ({q})" for p, q in sorted_items]
        values = [q for p, q in sorted_items]

        plt.figure(figsize=(10, 7))

        wedges, texts, autotexts = plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=self.colors[: len(values)],
            textprops={"color": self.text_color},
            wedgeprops={"edgecolor": self.bg_color, "linewidth": 1},
        )

        plt.setp(autotexts, size=10, weight="bold", color="white")
        plt.setp(texts, size=11)

        self._configurar_estilo("Jogos Zerados por Plataforma")
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

        medias = {p: sum(ns) / len(ns) for p, ns in notas_por_plat.items()}
        sorted_items = sorted(medias.items(), key=lambda x: x[1], reverse=True)
        plataformas = [x[0] for x in sorted_items]
        valores = [x[1] for x in sorted_items]

        plt.figure(figsize=(11, 6))

        bars = plt.bar(
            plataformas, valores, color=self.colors[0], edgecolor=self.plot_bg, zorder=3
        )

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.1,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                color=self.text_color,
                fontweight="bold",
            )

        self._configurar_estilo("Média de Notas por Plataforma", ylabel="Nota Média")
        plt.xticks(rotation=45)
        plt.ylim(0, 11)
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

        sorted_items = sorted(tempo_por_plat.items(), key=lambda x: x[1], reverse=True)
        plataformas = [x[0] for x in sorted_items]
        horas = [x[1] // 60 for x in sorted_items]

        plt.figure(figsize=(11, 6))

        bars = plt.bar(
            plataformas, horas, color=self.colors[1], edgecolor=self.plot_bg, zorder=3
        )

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + (max(horas) * 0.01),
                f"{height}h",
                ha="center",
                va="bottom",
                color=self.text_color,
                fontweight="bold",
            )

        self._configurar_estilo("Tempo Total (Horas) por Plataforma", ylabel="Horas")
        plt.xticks(rotation=45)
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

        plt.figure(figsize=(10, 6))

        bars = plt.bar(
            anos, qtd, color=self.colors[5], edgecolor=self.plot_bg, zorder=3
        )

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.1,
                f"{int(height)}",
                ha="center",
                va="bottom",
                color=self.text_color,
                fontweight="bold",
            )

        self._configurar_estilo(
            "Jogos Zerados por Ano", xlabel="Ano", ylabel="Quantidade"
        )
        plt.xticks(anos, rotation=45)
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

        plt.figure(figsize=(11, 6))

        for i, g in enumerate(generos):
            valores = [dados.get(a, {}).get(g, 0) for a in anos]
            color = self.colors[i % len(self.colors)]
            plt.plot(
                anos, valores, marker="o", label=g, color=color, linewidth=2, zorder=3
            )

        plt.legend(
            facecolor=self.plot_bg,
            edgecolor=self.grid_color,
            labelcolor=self.text_color,
        )
        self._configurar_estilo(
            "Comparação de Gêneros por Ano", xlabel="Ano", ylabel="Quantidade"
        )
        plt.xticks(anos)
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

        plt.bar(
            contagem.keys(),
            contagem.values(),
            color=self.colors[0],
            edgecolor=self.plot_bg,
            zorder=3,
            alpha=0.8,
        )

        plt.axhline(
            y=media,
            color=self.colors[2],
            linestyle="--",
            linewidth=2,
            label=f"Média Geral: {media:.2f}",
            zorder=4,
        )

        plt.legend(
            facecolor=self.plot_bg,
            edgecolor=self.grid_color,
            labelcolor=self.text_color,
        )
        self._configurar_estilo(
            "Distribuição de Notas", xlabel="Nota", ylabel="Quantidade de Jogos"
        )
        plt.xticks(range(1, 11))
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

        sorted_items = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        labels = [f"{k} ({v})" for k, v in sorted_items]
        values = [v for k, v in sorted_items]

        plt.figure(figsize=(10, 8))

        wedges, texts, autotexts = plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=self.colors[: len(values)],
            textprops={"color": self.text_color},
            wedgeprops={"edgecolor": self.bg_color, "linewidth": 1},
        )

        plt.setp(autotexts, size=9, weight="bold", color="white")

        self._configurar_estilo("Distribuição de Gêneros")
        plt.axis("equal")
        plt.show()
        return True
