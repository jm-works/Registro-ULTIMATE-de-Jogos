import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkFont
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.utils import centralizar_janela, calcular_total_minutos
from src.constantes import WALLPAPER_PATH, ASSETS_DIR
from src.gui.componentes import estilizar_botao


class JanelaChecklist:
    def __init__(self, root, gerenciador_dados):
        self.top = tk.Toplevel(root)
        self.top.title("Tarefas")
        self.top.geometry("500x600")
        self.top.resizable(True, True)
        centralizar_janela(self.top, 500, 600)

        self.dados = gerenciador_dados
        self.tarefas = self.dados.carregar_tarefas()

        self._criar_interface()

    def _criar_interface(self):
        tk.Label(
            self.top, text="Checklist de Tarefas", font=("Arial", 16, "bold")
        ).pack(pady=10)

        frame_lista = tk.Frame(self.top)
        frame_lista.pack(pady=10, fill="both", expand=True)

        self.listbox = tk.Listbox(frame_lista, width=50, height=15, font=("Arial", 11))
        self.listbox.pack(side="left", fill="both", expand=True, padx=10)

        sb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        frame_acoes = tk.Frame(self.top)
        frame_acoes.pack(pady=10)

        tk.Label(frame_acoes, text="Nova Tarefa:").grid(row=0, column=0, padx=5)
        self.entry_tarefa = tk.Entry(frame_acoes, width=25)
        self.entry_tarefa.grid(row=0, column=1, padx=5)

        btn_add = tk.Button(
            frame_acoes, text="Adicionar", command=self.adicionar_tarefa
        )
        estilizar_botao(btn_add, "gray", largura=12, altura=1)
        btn_add.grid(row=0, column=2, padx=5)

        frame_botoes = tk.Frame(self.top)
        frame_botoes.pack(pady=10)

        btn_ger = tk.Button(
            frame_botoes, text="Gerenciar Missões", command=self.gerenciar_missoes
        )
        estilizar_botao(btn_ger, "#4a90e2", largura=20, altura=1)
        btn_ger.grid(row=0, column=0, padx=10)

        btn_del = tk.Button(
            frame_botoes, text="Excluir Tarefa", command=self.excluir_tarefa
        )
        estilizar_botao(btn_del, "#f44336", largura=20, altura=1)
        btn_del.grid(row=0, column=1, padx=10)

        self.atualizar_lista()

    def atualizar_lista(self):
        self.listbox.delete(0, tk.END)
        for t in self.tarefas:
            missoes = t.get("missoes", [])
            completo = missoes and all(m.get("concluido", False) for m in missoes)

            status_icon = "🏆" if completo else "📝"
            if not missoes:
                status_icon = "📂"

            total = len(missoes)
            feitos = len([m for m in missoes if m.get("concluido", False)])
            progresso = f"({feitos}/{total})" if total > 0 else ""

            self.listbox.insert(tk.END, f"{status_icon} {t['nome']} {progresso}")

    def adicionar_tarefa(self):
        nome = self.entry_tarefa.get().strip()
        if nome:
            self.tarefas.append({"nome": nome, "missoes": []})
            self.dados.salvar_tarefas(self.tarefas)
            self.atualizar_lista()
            self.entry_tarefa.delete(0, tk.END)

    def excluir_tarefa(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        if messagebox.askyesno(
            "Confirmar", "Excluir esta tarefa e todas as suas missões?"
        ):
            self.tarefas.pop(sel[0])
            self.dados.salvar_tarefas(self.tarefas)
            self.atualizar_lista()

    def gerenciar_missoes(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Erro", "Selecione uma tarefa primeiro.")
            return

        index = sel[0]
        tarefa_selecionada = self.tarefas[index]

        def salvar_callback():
            self.dados.salvar_tarefas(self.tarefas)
            self.atualizar_lista()

        JanelaMissoes(self.top, tarefa_selecionada, salvar_callback)


class JanelaMissoes:
    def __init__(self, parent, tarefa, callback_salvar):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Missões: {tarefa['nome']}")
        self.top.geometry("450x550")
        self.top.resizable(True, True)
        centralizar_janela(self.top, 450, 550)

        self.tarefa = tarefa
        self.callback_salvar = callback_salvar

        if "missoes" not in self.tarefa:
            self.tarefa["missoes"] = []

        self._criar_interface()

    def _criar_interface(self):
        tk.Label(
            self.top,
            text=f"Missões de {self.tarefa['nome']}",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        frame_input = tk.Frame(self.top)
        frame_input.pack(pady=5)

        self.entry_missao = tk.Entry(frame_input, width=30)
        self.entry_missao.grid(row=0, column=0, padx=5)

        btn_add = tk.Button(frame_input, text="Adicionar", command=self.adicionar)
        estilizar_botao(btn_add, "gray", largura=10, altura=1)
        btn_add.grid(row=0, column=1, padx=5)

        frame_lista = tk.Frame(self.top)
        frame_lista.pack(pady=10, fill="both", expand=True)

        self.listbox = tk.Listbox(frame_lista, width=50, height=15, font=("Arial", 11))
        self.listbox.pack(side="left", fill="both", expand=True, padx=10)

        sb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.listbox.bind("<Double-Button-1>", self.toggle_missao)

        frame_btns = tk.Frame(self.top)
        frame_btns.pack(pady=10)

        btn_toggle = tk.Button(
            frame_btns, text="Concluir / Reabrir", command=self.toggle_missao
        )
        estilizar_botao(btn_toggle, "#27AE60", largura=18, altura=1)
        btn_toggle.grid(row=0, column=0, padx=5)

        btn_del = tk.Button(frame_btns, text="Remover Missão", command=self.remover)
        estilizar_botao(btn_del, "#e74c3c", largura=18, altura=1)
        btn_del.grid(row=0, column=1, padx=5)

        self.atualizar_lista()

    def atualizar_lista(self):
        self.listbox.delete(0, tk.END)
        for m in self.tarefa["missoes"]:
            status = "☑" if m.get("concluido") else "☐"
            texto = m.get("descricao", "")
            self.listbox.insert(tk.END, f"{status} {texto}")

    def adicionar(self):
        texto = self.entry_missao.get().strip()
        if texto:
            self.tarefa["missoes"].append({"descricao": texto, "concluido": False})
            self.callback_salvar()
            self.atualizar_lista()
            self.entry_missao.delete(0, tk.END)

    def toggle_missao(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return

        idx = sel[0]
        estado_atual = self.tarefa["missoes"][idx].get("concluido", False)
        self.tarefa["missoes"][idx]["concluido"] = not estado_atual

        self.callback_salvar()
        self.atualizar_lista()

        self.listbox.selection_set(idx)

    def remover(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        idx = sel[0]
        self.tarefa["missoes"].pop(idx)
        self.callback_salvar()
        self.atualizar_lista()


class JanelaResumo:
    def __init__(self, root, lista_jogos):
        self.top = tk.Toplevel(root)
        self.top.title("Dashboard de Resumo")
        self.top.geometry("900x650")
        self.top.resizable(True, True)
        centralizar_janela(self.top, 900, 650)

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#ffffff"
        self.accent_color = "#4a90e2"
        self.top.configure(bg=self.bg_color)

        self.jogos = lista_jogos
        self.zerados = [j for j in self.jogos if j.get("Data de Zeramento")]

        self._calcular_dados()
        self._criar_interface()

    def _calcular_dados(self):
        self.total_zerados = len(self.zerados)
        self.total_jogos = len(self.jogos)

        minutos_totais = sum(
            calcular_total_minutos(j.get("Tempo Jogado", "0:00")) for j in self.zerados
        )
        self.horas_totais = minutos_totais // 60

        notas = [float(j["Nota"]) for j in self.zerados if j.get("Nota")]
        self.media_notas = sum(notas) / len(notas) if notas else 0.0

        generos = [j["Gênero"] for j in self.zerados]
        self.top_genero = max(set(generos), key=generos.count) if generos else "N/A"

        self.top_5_jogos = sorted(
            self.zerados,
            key=lambda x: float(x["Nota"]) if x.get("Nota") else 0,
            reverse=True,
        )[:5]

    def _criar_interface(self):
        lbl_titulo = tk.Label(
            self.top,
            text="Visão Geral da Biblioteca",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        lbl_titulo.pack(pady=(15, 20))

        main_frame = tk.Frame(self.top, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        frame_cards = tk.Frame(main_frame, bg=self.bg_color)
        frame_cards.pack(fill="x", pady=10)

        self._criar_card(frame_cards, "Jogos Zerados", f"{self.total_zerados}", "🏆", 0)
        self._criar_card(frame_cards, "Tempo Total", f"{self.horas_totais}h", "⏳", 1)
        self._criar_card(frame_cards, "Média Notas", f"{self.media_notas:.2f}", "⭐", 2)
        self._criar_card(frame_cards, "Gênero Favorito", f"{self.top_genero}", "🎮", 3)

        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True, pady=10)

        left_frame = tk.Frame(content_frame, bg=self.card_bg, padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            left_frame,
            text="Distribuição de Status",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
        ).pack(pady=5)

        self._criar_grafico_pizza(left_frame)

        # Lado Direito: Top 5 Melhores Jogos
        right_frame = tk.Frame(content_frame, bg=self.card_bg, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            right_frame,
            text="Top 5 - Melhores Avaliados",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
        ).pack(pady=5)

        self._criar_tabela_top5(right_frame)

    def _criar_card(self, parent, titulo, valor, icone, col_index):
        card = tk.Frame(parent, bg=self.card_bg, relief="flat", bd=1)
        card.grid(row=0, column=col_index, padx=10, sticky="ew")
        parent.grid_columnconfigure(col_index, weight=1)

        tk.Label(
            card, text=icone, font=("Arial", 24), bg=self.card_bg, fg=self.accent_color
        ).pack(pady=(10, 0))
        tk.Label(
            card,
            text=valor,
            font=("Arial", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
        ).pack()
        tk.Label(
            card, text=titulo, font=("Arial", 10), bg=self.card_bg, fg="#aaaaaa"
        ).pack(pady=(0, 10))

    def _criar_grafico_pizza(self, parent):
        status_counts = {}
        for j in self.jogos:
            s = j["Forma de Zeramento"]
            status_counts[s] = status_counts.get(s, 0) + 1

        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors = ["#4a90e2", "#2ecc71", "#f1c40f", "#e74c3c", "#95a5a6"]

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor(self.card_bg)
        ax.set_facecolor(self.card_bg)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors[: len(labels)],
        )

        plt.setp(texts, color="white")
        plt.setp(autotexts, size=8, weight="bold", color="white")

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _criar_tabela_top5(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=self.bg_color,
            foreground="white",
            fieldbackground=self.bg_color,
            rowheight=25,
        )
        style.map("Treeview", background=[("selected", self.accent_color)])
        style.configure(
            "Treeview.Heading", background="#444", foreground="white", relief="flat"
        )

        cols = ("Jogo", "Nota", "Plat.")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=8)

        tree.heading("Jogo", text="Nome do Jogo")
        tree.heading("Nota", text="Nota")
        tree.heading("Plat.", text="Plataforma")

        tree.column("Jogo", width=150)
        tree.column("Nota", width=50, anchor="center")
        tree.column("Plat.", width=80, anchor="center")

        for jogo in self.top_5_jogos:
            tree.insert(
                "", "end", values=(jogo["Título"], jogo["Nota"], jogo["Plataforma"])
            )

        tree.pack(fill="both", expand=True, pady=10)


class JanelaWallpaper:
    def __init__(self, root, callback_atualizar):
        self.root = root
        self.callback = callback_atualizar
        self.caminho_imagem = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")]
        )
        if self.caminho_imagem:
            self._abrir_editor()

    def _abrir_editor(self):
        self.top = tk.Toplevel(self.root)
        self.top.title("Editar Wallpaper")
        self.top.geometry("900x700")
        centralizar_janela(self.top, 900, 700)

        self.img_orig = Image.open(self.caminho_imagem)
        fator = min(800 / self.img_orig.width, 550 / self.img_orig.height)
        novos_dims = (
            int(self.img_orig.width * fator),
            int(self.img_orig.height * fator),
        )
        self.img_show = self.img_orig.resize(novos_dims, Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(self.img_show)

        self.canvas = tk.Canvas(self.top, width=novos_dims[0], height=novos_dims[1])
        self.canvas.pack(pady=10)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

        btn = tk.Button(
            self.top, text="Salvar (Recorte Automático 600x400)", command=self._salvar
        )
        estilizar_botao(btn, "#27AE60", largura=30)
        btn.pack(pady=10)

    def _salvar(self):
        target = self.img_orig.resize((600, 400), Image.LANCZOS)

        os.makedirs(os.path.dirname(WALLPAPER_PATH), exist_ok=True)
        target.save(WALLPAPER_PATH, "PNG")

        messagebox.showinfo("Sucesso", "Wallpaper atualizado!")
        self.callback()
        self.top.destroy()
