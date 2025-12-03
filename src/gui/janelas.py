import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkFont
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.utils import centralizar_janela, calcular_total_minutos
from src.constantes import WALLPAPER_PATH, GENEROS
from src.gui.componentes import estilizar_botao


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg_color="#1e1e1e", *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Enter>", self._bound_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbound_to_mousewheel)
        self.bind("<Destroy>", self._on_destroy)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_destroy(self, event):
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except:
            pass

    def _on_mousewheel(self, event):
        try:
            start, end = self.canvas.yview()

            if start <= 0.0 and end >= 1.0:
                return

            delta = int(-1 * (event.delta / 120))

            if delta < 0 and start <= 0.0:
                return

            if delta > 0 and end >= 1.0:
                return

            self.canvas.yview_scroll(delta, "units")
        except tk.TclError:
            pass


class JanelaSeletorGenero:
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Selecionar Gênero")
        self.top.geometry("320x450")
        centralizar_janela(self.top, 320, 450)
        self.top.configure(bg="#1e1e1e")
        self.top.resizable(False, False)

        self.callback = callback
        self.lista_completa = GENEROS

        self._criar_ui()

        self.top.transient(parent)
        self.top.grab_set()
        self.top.focus_set()

    def _criar_ui(self):
        tk.Label(
            self.top,
            text="Pesquisar Gênero:",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=(15, 5))

        self.var_busca = tk.StringVar()
        self.var_busca.trace("w", self._filtrar)

        entry = tk.Entry(
            self.top,
            textvariable=self.var_busca,
            font=("Arial", 11),
            bg="#333",
            fg="white",
            insertbackground="white",
        )
        entry.pack(fill="x", padx=20, pady=5)
        entry.focus_set()

        frame_list = tk.Frame(self.top, bg="#1e1e1e")
        frame_list.pack(fill="both", expand=True, padx=20, pady=10)

        sb = tk.Scrollbar(frame_list)
        sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            frame_list,
            yscrollcommand=sb.set,
            height=15,
            bg="#2d2d2d",
            fg="white",
            selectbackground="#4a90e2",
            font=("Arial", 10),
            bd=0,
            highlightthickness=0,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self._selecionar)
        self.listbox.bind("<Return>", self._selecionar)

        btn = tk.Button(
            self.top,
            text="Confirmar Seleção",
            command=self._selecionar,
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
        )
        btn.pack(fill="x", padx=20, pady=(0, 20))

        self._atualizar_lista(self.lista_completa)

    def _filtrar(self, *args):
        termo = self.var_busca.get().lower()
        if not termo:
            filtrados = self.lista_completa
        else:
            filtrados = [g for g in self.lista_completa if termo in g.lower()]
        self._atualizar_lista(filtrados)

    def _atualizar_lista(self, itens):
        self.listbox.delete(0, tk.END)
        for item in itens:
            self.listbox.insert(tk.END, item)

    def _selecionar(self, event=None):
        sel = self.listbox.curselection()
        if sel:
            escolhido = self.listbox.get(sel[0])
            self.callback(escolhido)
            self.top.destroy()
        else:
            if self.listbox.size() == 1:
                escolhido = self.listbox.get(0)
                self.callback(escolhido)
                self.top.destroy()


class JanelaChecklist:
    def __init__(self, root, gerenciador_dados):
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciador de Tarefas")
        self.top.geometry("550x700")
        centralizar_janela(self.top, 550, 700)

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#ffffff"
        self.accent_color = "#4a90e2"
        self.success_color = "#27AE60"

        self.top.configure(bg=self.bg_color)

        self.dados = gerenciador_dados
        self.tarefas = self.dados.carregar_tarefas()

        self._criar_interface()

    def _criar_interface(self):
        tk.Label(
            self.top,
            text="Meus Projetos & Tarefas",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(pady=(20, 10))

        frame_add = tk.Frame(self.top, bg=self.bg_color)
        frame_add.pack(pady=10, fill="x", padx=20)

        self.entry_nova = tk.Entry(
            frame_add,
            font=("Arial", 11),
            bg="#3d3d3d",
            fg="white",
            insertbackground="white",
            relief="flat",
        )
        self.entry_nova.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.entry_nova.bind("<Return>", lambda e: self.adicionar_tarefa())

        btn_add = tk.Button(
            frame_add,
            text="+ Criar",
            command=self.adicionar_tarefa,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
        )
        btn_add.pack(side="right", ipadx=10, ipady=2)

        ttk.Separator(self.top, orient="horizontal").pack(fill="x", padx=20, pady=10)

        self.container = ScrollableFrame(self.top, bg_color=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.container.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.tarefas:
            tk.Label(
                self.container.scrollable_frame,
                text="Nenhuma tarefa encontrada.",
                bg=self.bg_color,
                fg="#777",
                font=("Arial", 12),
            ).pack(pady=20)
            return

        for i, tarefa in enumerate(self.tarefas):
            self._criar_card_tarefa(i, tarefa)

    def _criar_card_tarefa(self, index, tarefa):
        missoes = tarefa.get("missoes", [])
        total = len(missoes)
        concluidas = len([m for m in missoes if m.get("concluido")])

        card = tk.Frame(
            self.container.scrollable_frame, bg=self.card_bg, padx=15, pady=10
        )
        card.pack(fill="x", pady=5, padx=5)

        header = tk.Frame(card, bg=self.card_bg)
        header.pack(fill="x")

        status_icon = "🏆" if (total > 0 and total == concluidas) else "📝"
        lbl_titulo = tk.Label(
            header,
            text=f"{status_icon} {tarefa['nome']}",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            anchor="w",
        )
        lbl_titulo.pack(side="left", fill="x", expand=True)

        btn_edit = tk.Button(
            header,
            text="⚙️ Detalhes",
            font=("Arial", 9),
            bg="#3d3d3d",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: self.abrir_detalhes(index),
        )
        btn_edit.pack(side="right", padx=5)

        btn_del = tk.Button(
            header,
            text="🗑️",
            font=("Arial", 9),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: self.excluir_tarefa(index),
        )
        btn_del.pack(side="right")

        if total > 0:
            frame_prog = tk.Frame(card, bg=self.card_bg)
            frame_prog.pack(fill="x", pady=(10, 0))

            porcentagem = (concluidas / total) * 100

            style = ttk.Style()
            style.theme_use("clam")
            style.configure(
                "green.Horizontal.TProgressbar",
                background=self.success_color,
                troughcolor="#1e1e1e",
                bordercolor=self.card_bg,
                lightcolor=self.success_color,
                darkcolor=self.success_color,
            )

            pb = ttk.Progressbar(
                frame_prog,
                style="green.Horizontal.TProgressbar",
                length=100,
                mode="determinate",
                value=porcentagem,
            )
            pb.pack(side="left", fill="x", expand=True, padx=(0, 10))

            lbl_prog = tk.Label(
                frame_prog,
                text=f"{concluidas}/{total} ({int(porcentagem)}%)",
                bg=self.card_bg,
                fg="#aaaaaa",
                font=("Arial", 9),
            )
            lbl_prog.pack(side="right")
        else:
            tk.Label(
                card,
                text="Sem sub-tarefas",
                bg=self.card_bg,
                fg="#555",
                font=("Arial", 8, "italic"),
                anchor="w",
            ).pack(fill="x", pady=(5, 0))

    def adicionar_tarefa(self):
        nome = self.entry_nova.get().strip()
        if nome:
            self.tarefas.append({"nome": nome, "missoes": []})
            self.dados.salvar_tarefas(self.tarefas)
            self.atualizar_lista()
            self.entry_nova.delete(0, tk.END)

    def excluir_tarefa(self, index):
        if messagebox.askyesno("Confirmar", "Excluir esta tarefa?"):
            self.tarefas.pop(index)
            self.dados.salvar_tarefas(self.tarefas)
            self.atualizar_lista()

    def abrir_detalhes(self, index):
        def ao_fechar():
            self.dados.salvar_tarefas(self.tarefas)
            self.atualizar_lista()

        JanelaMissoes(self.top, self.tarefas[index], ao_fechar)


class JanelaMissoes:
    def __init__(self, parent, tarefa, callback_fechar):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Detalhes: {tarefa['nome']}")
        self.top.geometry("450x600")
        centralizar_janela(self.top, 450, 600)

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#ffffff"
        self.top.configure(bg=self.bg_color)

        self.tarefa = tarefa
        self.callback_fechar = callback_fechar

        if "missoes" not in self.tarefa:
            self.tarefa["missoes"] = []

        self._criar_interface()

        self.top.protocol("WM_DELETE_WINDOW", self._fechar)

    def _fechar(self):
        self.callback_fechar()
        self.top.destroy()

    def _criar_interface(self):
        header = tk.Frame(self.top, bg=self.bg_color)
        header.pack(fill="x", padx=20, pady=20)

        tk.Label(
            header,
            text=self.tarefa["nome"],
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            wraplength=400,
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Lista de verificação",
            font=("Arial", 10),
            bg=self.bg_color,
            fg="#aaaaaa",
        ).pack(anchor="w")

        frame_input = tk.Frame(self.top, bg=self.bg_color)
        frame_input.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_missao = tk.Entry(
            frame_input,
            font=("Arial", 11),
            bg="#3d3d3d",
            fg="white",
            insertbackground="white",
            relief="flat",
        )
        self.entry_missao.pack(
            side="left", fill="x", expand=True, padx=(0, 10), ipady=5
        )
        self.entry_missao.bind("<Return>", lambda e: self.adicionar())

        btn_add = tk.Button(
            frame_input,
            text="+",
            command=self.adicionar,
            bg="#4a90e2",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
        )
        btn_add.pack(side="right", ipadx=10)

        self.container = ScrollableFrame(self.top, bg_color=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.container.scrollable_frame.winfo_children():
            widget.destroy()

        missoes = self.tarefa["missoes"]

        if not missoes:
            tk.Label(
                self.container.scrollable_frame,
                text="Nenhuma etapa adicionada.",
                bg=self.bg_color,
                fg="#555",
            ).pack(pady=20)
            return

        for i, missao in enumerate(missoes):
            self._criar_item_missao(i, missao)

    def _criar_item_missao(self, index, missao):
        frame = tk.Frame(
            self.container.scrollable_frame, bg=self.card_bg, pady=5, padx=5
        )
        frame.pack(fill="x", pady=2, padx=5)

        status = "☑" if missao.get("concluido") else "☐"
        color = "#2ecc71" if missao.get("concluido") else "#7f8c8d"

        btn_check = tk.Label(
            frame,
            text=status,
            font=("Arial", 14),
            bg=self.card_bg,
            fg=color,
            cursor="hand2",
        )
        btn_check.pack(side="left", padx=5)
        btn_check.bind("<Button-1>", lambda e: self.toggle_missao(index))

        texto_style = (
            ("Arial", 11, "overstrike") if missao.get("concluido") else ("Arial", 11)
        )
        texto_color = "#777" if missao.get("concluido") else self.text_color

        lbl_text = tk.Label(
            frame,
            text=missao["descricao"],
            font=texto_style,
            bg=self.card_bg,
            fg=texto_color,
            anchor="w",
        )
        lbl_text.pack(side="left", fill="x", expand=True, padx=5)
        lbl_text.bind("<Button-1>", lambda e: self.toggle_missao(index))

        btn_del = tk.Label(
            frame,
            text="✕",
            font=("Arial", 10, "bold"),
            bg=self.card_bg,
            fg="#e74c3c",
            cursor="hand2",
        )
        btn_del.pack(side="right", padx=10)
        btn_del.bind("<Button-1>", lambda e: self.remover(index))

    def adicionar(self):
        texto = self.entry_missao.get().strip()
        if texto:
            self.tarefa["missoes"].append({"descricao": texto, "concluido": False})
            self.atualizar_lista()
            self.entry_missao.delete(0, tk.END)

    def toggle_missao(self, index):
        estado_atual = self.tarefa["missoes"][index].get("concluido", False)
        self.tarefa["missoes"][index]["concluido"] = not estado_atual
        self.atualizar_lista()

    def remover(self, index):
        self.tarefa["missoes"].pop(index)
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
