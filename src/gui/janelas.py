import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
from tkinter import font as tkFont
from PIL import Image, ImageTk
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import webbrowser
import urllib.parse
import pyperclip

from src.utils import centralizar_janela, calcular_total_minutos
from src.constantes import WALLPAPER_PATH, GENEROS, PLATAFORMAS
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


class JanelaEditorDescricao:
    def __init__(self, parent, texto_atual, callback_salvar, limite_chars=2000):
        self.top = tk.Toplevel(parent)
        self.top.title("Editor de Descrição")
        self.top.geometry("600x500")
        centralizar_janela(self.top, 600, 550)
        self.top.configure(bg="#1e1e1e")
        self.top.resizable(False, False)

        self.callback = callback_salvar
        self.limite = limite_chars
        self.texto_inicial = texto_atual

        self._criar_ui()

        self.top.transient(parent)
        self.top.grab_set()
        self.text_area.focus_set()

    def _criar_ui(self):
        frame_toolbar = tk.Frame(self.top, bg="#2d2d2d", pady=5)
        frame_toolbar.pack(fill="x")

        btn_bold = tk.Button(
            frame_toolbar,
            text="N",
            font=("Arial", 10, "bold"),
            width=3,
            bg="#333",
            fg="white",
            relief="raised",
            command=lambda: self._inserir_tag("**"),
        )
        btn_bold.pack(side="left", padx=(10, 5))

        btn_italic = tk.Button(
            frame_toolbar,
            text="I",
            font=("Arial", 10, "italic"),
            width=3,
            bg="#333",
            fg="white",
            relief="raised",
            command=lambda: self._inserir_tag("*"),
        )
        btn_italic.pack(side="left", padx=5)

        tk.Label(
            frame_toolbar,
            text="| Use Markdown: **negrito**, *itálico*",
            bg="#2d2d2d",
            fg="#aaaaaa",
            font=("Arial", 9),
        ).pack(side="left", padx=10)

        frame_text = tk.Frame(self.top, bg="#1e1e1e", padx=10, pady=5)
        frame_text.pack(fill="both", expand=True)

        self.text_area = tk.Text(
            frame_text,
            bg="#2d2d2d",
            fg="#eeeeee",
            font=("Arial", 11),
            wrap="word",
            bd=0,
            highlightthickness=1,
            highlightbackground="#4a90e2",
            insertbackground="white",
            padx=10,
            pady=10,
        )
        self.text_area.pack(side="left", fill="both", expand=True)
        self.text_area.insert("1.0", self.texto_inicial)

        sb = tk.Scrollbar(frame_text, command=self.text_area.yview)
        sb.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=sb.set)

        self.text_area.bind("<KeyRelease>", self._atualizar_contador)
        self.text_area.bind("<KeyPress>", self._verificar_limite)
        self.text_area.bind("<<Paste>>", self._ao_colar)

        frame_footer = tk.Frame(self.top, bg="#1e1e1e", pady=10)
        frame_footer.pack(fill="x", padx=10)

        self.lbl_contador = tk.Label(
            frame_footer,
            text=f"0 / {self.limite}",
            bg="#1e1e1e",
            fg="#aaaaaa",
            font=("Arial", 9),
        )
        self.lbl_contador.pack(side="left", pady=5)

        btn_salvar = tk.Button(
            frame_footer, text="Salvar Descrição", command=self._salvar
        )
        estilizar_botao(btn_salvar, "#27AE60", largura=30, altura=2)
        btn_salvar.pack(side="right")

        self._atualizar_contador()

    def _inserir_tag(self, tag):
        conteudo = self.text_area.get("1.0", "end-1c")
        if len(conteudo) + (len(tag) * 2) > self.limite:
            messagebox.showwarning("Limite", "Espaço insuficiente para formatar.")
            return

        try:
            sel_start = self.text_area.index("sel.first")
            sel_end = self.text_area.index("sel.last")
            texto_sel = self.text_area.get(sel_start, sel_end)
            self.text_area.delete(sel_start, sel_end)
            self.text_area.insert(sel_start, f"{tag}{texto_sel}{tag}")
        except tk.TclError:
            self.text_area.insert(tk.INSERT, f"{tag}texto{tag}")
        self._atualizar_contador()

    def _verificar_limite(self, event):
        teclas_permitidas = ["BackSpace", "Delete", "Left", "Right", "Up", "Down"]

        if event.keysym in teclas_permitidas:
            return

        conteudo = self.text_area.get("1.0", "end-1c")
        if len(conteudo) >= self.limite:
            if not (event.state & 4):
                return "break"

    def _ao_colar(self, event):
        try:
            texto_clip = self.top.clipboard_get()
        except:
            return "break"

        conteudo_atual = self.text_area.get("1.0", "end-1c")
        espaco_restante = self.limite - len(conteudo_atual)

        if espaco_restante <= 0:
            return "break"

        if len(texto_clip) > espaco_restante:
            self.text_area.insert(tk.INSERT, texto_clip[:espaco_restante])
            self._atualizar_contador()
            return "break"

        self.top.after(10, self._atualizar_contador)

    def _atualizar_contador(self, event=None):
        conteudo = self.text_area.get("1.0", "end-1c")
        tamanho = len(conteudo)
        self.lbl_contador.config(text=f"{tamanho} / {self.limite}")
        self.lbl_contador.config(fg="#e74c3c" if tamanho >= self.limite else "#aaaaaa")

    def _salvar(self):
        texto = self.text_area.get("1.0", "end-1c").strip()
        self.callback(texto)
        self.top.destroy()


class JanelaDetalhes:
    def __init__(self, parent, jogo):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Detalhes: {jogo['Título']}")
        self.top.geometry("600x650")
        centralizar_janela(self.top, 600, 650)

        self.bg_color = "#1e1e1e"
        self.fg_color = "white"
        self.accent_color = "#4a90e2"

        self.top.configure(bg=self.bg_color)
        self.jogo = jogo

        self._criar_ui()

    def _criar_ui(self):
        frame_header = tk.Frame(self.top, bg=self.bg_color)
        frame_header.pack(fill="x", padx=20, pady=20)

        lbl_titulo = tk.Label(
            frame_header,
            text=self.jogo["Título"],
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color,
            wraplength=550,
            justify="center",
        )
        lbl_titulo.pack()

        destaque = "💎 HIDDEN GEM" if self.jogo.get("Hidden Gem") else ""
        if destaque:
            tk.Label(
                frame_header,
                text=destaque,
                font=("Arial", 11, "bold"),
                bg=self.bg_color,
                fg="#9b59b6",
            ).pack(pady=(5, 0))

        frame_info = tk.Frame(self.top, bg=self.bg_color)
        frame_info.pack(fill="x", padx=40, pady=10)

        dados = [
            ("Gênero:", self.jogo["Gênero"]),
            ("Plataforma:", self.jogo["Plataforma"]),
            ("Estado:", self.jogo["Forma de Zeramento"]),
            ("Data:", self.jogo.get("Data de Zeramento", "-")),
            ("Tempo:", self.jogo.get("Tempo Jogado", "-")),
            ("Nota:", str(self.jogo.get("Nota", "-"))),
        ]

        for i, (label, valor) in enumerate(dados):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(
                frame_info,
                text=label,
                font=("Arial", 10, "bold"),
                bg=self.bg_color,
                fg="#888888",
            ).grid(row=row, column=col, sticky="w", pady=8)

            tk.Label(
                frame_info, text=valor, font=("Arial", 11), bg=self.bg_color, fg="white"
            ).grid(row=row, column=col + 1, sticky="w", padx=(5, 30), pady=8)

        tk.Label(
            self.top,
            text="Descrição / Comentários:",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg="white",
        ).pack(anchor="w", padx=20, pady=(20, 5))

        frame_desc = tk.Frame(self.top, bg="#2d2d2d")
        frame_desc.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.txt_desc = tk.Text(
            frame_desc,
            bg="#2d2d2d",
            fg="#dddddd",
            font=("Arial", 11),
            wrap="word",
            bd=0,
            padx=15,
            pady=15,
            highlightthickness=0,
        )
        self.txt_desc.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(frame_desc, command=self.txt_desc.yview)
        sb.pack(side="right", fill="y")
        self.txt_desc.config(yscrollcommand=sb.set)

        descricao = self.jogo.get(
            "Descrição de Zeramento", "Nenhuma descrição informada."
        )
        self.txt_desc.insert("1.0", descricao)

        self._aplicar_formatacao()
        self.txt_desc.config(state="disabled")

    def _aplicar_formatacao(self):
        self.txt_desc.tag_configure("bold", font=("Arial", 11, "bold"))
        self.txt_desc.tag_configure("italic", font=("Arial", 11, "italic"))

        self._processar_tag(r"\*\*(.*?)\*\*", "bold", 2)
        self._processar_tag(r"\*(.*?)\*", "italic", 1)

    def _processar_tag(self, regex_pattern, tag_name, marker_len):
        while True:
            pos = self.txt_desc.search(
                regex_pattern, "1.0", stopindex="end", count=tk.IntVar(), regexp=True
            )
            if not pos:
                break

            count_var = tk.IntVar()
            self.txt_desc.search(
                regex_pattern, pos, stopindex="end", count=count_var, regexp=True
            )
            chars_match = count_var.get()
            if chars_match == 0:
                break

            end_pos = f"{pos}+{chars_match}c"
            full_text = self.txt_desc.get(pos, end_pos)
            inner_text = full_text[marker_len:-marker_len]

            self.txt_desc.delete(pos, end_pos)
            self.txt_desc.insert(pos, inner_text, tag_name)


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


class JanelaSeletorPlataforma:
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Selecionar Plataforma")
        self.top.geometry("320x450")
        centralizar_janela(self.top, 320, 450)
        self.top.configure(bg="#1e1e1e")
        self.top.resizable(False, False)

        self.callback = callback
        self.lista_completa = PLATAFORMAS

        self._criar_ui()

        self.top.transient(parent)
        self.top.grab_set()
        self.top.focus_set()

    def _criar_ui(self):
        tk.Label(
            self.top,
            text="Pesquisar Plataforma:",
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
            filtrados = [p for p in self.lista_completa if termo in p.lower()]
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
        self.dias_jogados = self.horas_totais / 24

        notas = [float(j["Nota"]) for j in self.zerados if j.get("Nota")]
        self.media_notas = sum(notas) / len(notas) if notas else 0.0
        generos = [j["Gênero"] for j in self.zerados]
        self.top_genero = max(set(generos), key=generos.count) if generos else "N/A"

        self.hidden_gems_list = [j for j in self.jogos if j.get("Hidden Gem")]

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
        self._criar_card(
            frame_cards,
            "Tempo Total",
            f"{self.horas_totais}h ({self.dias_jogados:.1f}d)",
            "⏳",
            1,
        )
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
            text="💎 Hidden Gems (Destaques)",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#9b59b6",
        ).pack(pady=5)
        self._criar_tabela_hidden_gems(right_frame)

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

        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor(self.card_bg)

        ax = fig.add_subplot(111)
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

    def _criar_tabela_hidden_gems(self, parent):
        frame_busca = tk.Frame(parent, bg=self.card_bg)
        frame_busca.pack(fill="x", pady=(0, 5))

        tk.Label(frame_busca, text="🔍", bg=self.card_bg, fg="#aaaaaa").pack(
            side="left", padx=(0, 5)
        )

        self.var_busca_gem = tk.StringVar()
        self.var_busca_gem.trace("w", self._filtrar_gems)

        entry = tk.Entry(
            frame_busca,
            textvariable=self.var_busca_gem,
            bg="#3d3d3d",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Arial", 10),
        )
        entry.pack(side="left", fill="x", expand=True)

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

        cols = ("Jogo", "Gênero", "Plat.")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=8)
        self.tree.heading("Jogo", text="Nome do Jogo")
        self.tree.heading("Gênero", text="Gênero")
        self.tree.heading("Plat.", text="Plataforma")
        self.tree.column("Jogo", width=150)
        self.tree.column("Gênero", width=80, anchor="center")
        self.tree.column("Plat.", width=80, anchor="center")

        sb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side="left", fill="both", expand=True, pady=10)
        sb.pack(side="right", fill="y", pady=10)

        self.tree.bind("<Button-3>", self._abrir_menu_contexto)
        self.tree.bind("<Double-Button-1>", self._on_double_click)

        self._atualizar_treeview(self.hidden_gems_list)

    def _filtrar_gems(self, *args):
        termo = self.var_busca_gem.get().lower()
        if not termo:
            filtrados = self.hidden_gems_list
        else:
            filtrados = [
                j
                for j in self.hidden_gems_list
                if termo in j["Título"].lower()
                or termo in j["Gênero"].lower()
                or termo in j["Plataforma"].lower()
            ]
        self._atualizar_treeview(filtrados)

    def _atualizar_treeview(self, lista):
        self.tree.delete(*self.tree.get_children())
        for jogo in lista:
            self.tree.insert(
                "", "end", values=(jogo["Título"], jogo["Gênero"], jogo["Plataforma"])
            )

    def _on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        values = self.tree.item(item_id, "values")
        titulo = values[0]
        jogo = next((j for j in self.hidden_gems_list if j["Título"] == titulo), None)

        if jogo:
            JanelaDetalhes(self.top, jogo)

    def _abrir_menu_contexto(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        self.tree.selection_set(item_id)
        values = self.tree.item(item_id, "values")
        titulo = values[0]

        jogo = next((j for j in self.hidden_gems_list if j["Título"] == titulo), None)

        if not jogo:
            return

        m = Menu(self.top, tearoff=0)
        m.add_command(
            label="📜 Ver Detalhes", command=lambda: JanelaDetalhes(self.top, jogo)
        )
        m.add_separator()
        m.add_command(label="📋 Copiar Nome", command=lambda: pyperclip.copy(titulo))
        m.add_command(
            label="🌍 Pesquisar no Google",
            command=lambda: webbrowser.open(
                f"https://www.google.com/search?q={urllib.parse.quote(titulo)}"
            ),
        )

        m.post(event.x_root, event.y_root)


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
