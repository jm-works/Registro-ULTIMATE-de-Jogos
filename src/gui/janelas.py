import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkFont
from PIL import Image, ImageTk
import os

from src.utils import centralizar_janela, calcular_total_minutos
from src.constantes import WALLPAPER_PATH, ASSETS_DIR
from src.gui.componentes import estilizar_botao


class JanelaChecklist:
    def __init__(self, root, gerenciador_dados):
        self.top = tk.Toplevel(root)
        self.top.title("Tarefas")
        self.top.geometry("500x500")
        self.top.resizable(False, False)
        centralizar_janela(self.top, 500, 500)

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
                status_icon = "📂"  # Ícone para pasta vazia

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
        self.top.geometry("450x500")
        self.top.resizable(False, False)
        centralizar_janela(self.top, 450, 500)

        self.tarefa = tarefa
        self.callback_salvar = callback_salvar

        # Garante que a lista de missões existe
        if "missoes" not in self.tarefa:
            self.tarefa["missoes"] = []

        self._criar_interface()

    def _criar_interface(self):
        tk.Label(
            self.top,
            text=f"Missões de {self.tarefa['nome']}",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Entrada
        frame_input = tk.Frame(self.top)
        frame_input.pack(pady=5)

        self.entry_missao = tk.Entry(frame_input, width=30)
        self.entry_missao.grid(row=0, column=0, padx=5)

        btn_add = tk.Button(frame_input, text="Adicionar", command=self.adicionar)
        estilizar_botao(btn_add, "gray", largura=10, altura=1)
        btn_add.grid(row=0, column=1, padx=5)

        # Lista
        frame_lista = tk.Frame(self.top)
        frame_lista.pack(pady=10, fill="both", expand=True)

        self.listbox = tk.Listbox(frame_lista, width=50, height=15, font=("Arial", 11))
        self.listbox.pack(side="left", fill="both", expand=True, padx=10)

        sb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.listbox.bind("<Double-Button-1>", self.toggle_missao)

        # Botões
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
        self.top.title("Resumo Geral")
        self.top.geometry("590x650")
        self.top.resizable(False, False)
        centralizar_janela(self.top, 590, 650)

        self.jogos = lista_jogos
        self._criar_interface()

    def _criar_interface(self):
        canvas = tk.Canvas(self.top, bg="black", width=570)
        sb = ttk.Scrollbar(self.top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="black")

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        zerados = [j for j in self.jogos if j.get("Data de Zeramento")]
        desistidos = [
            j for j in self.jogos if j.get("Forma de Zeramento") == "Desistência"
        ]
        planejados = [
            j for j in self.jogos if j.get("Forma de Zeramento") == "Planejo Jogar"
        ]

        notas = [float(j["Nota"]) for j in zerados if j.get("Nota")]
        media = sum(notas) / len(notas) if notas else 0

        fonte_tit = tkFont.Font(family="Arial", size=16, weight="bold")
        fonte_txt = tkFont.Font(family="Arial", size=14)

        lbls = [
            ("Resumo Geral", fonte_tit),
            (f"Jogos Zerados: {len(zerados)}", fonte_txt),
            (f"Jogos Desistidos: {len(desistidos)}", fonte_txt),
            (f"Jogos Planejados: {len(planejados)}", fonte_txt),
            (f"Média de Notas (Zerados): {media:.2f}", fonte_txt),
            ("Resumo por Gêneros:", fonte_tit),
        ]

        for txt, fonte in lbls:
            tk.Label(scroll_frame, text=txt, font=fonte, bg="black", fg="white").pack(
                pady=5
            )

        self._criar_tabela_generos(scroll_frame, zerados)

    def _criar_tabela_generos(self, parent, zerados):
        cols = ("Genero", "Qtd", "Tempo (h)")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=5)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("Genero", width=200)
        tree.column("Qtd", width=80)
        tree.column("Tempo (h)", width=100)

        contagem = {}
        for j in zerados:
            g = j["Gênero"]
            t = calcular_total_minutos(j.get("Tempo Jogado", "0:00"))
            if g not in contagem:
                contagem[g] = {"qtd": 0, "tempo": 0}
            contagem[g]["qtd"] += 1
            contagem[g]["tempo"] += t

        for g, d in contagem.items():
            tree.insert("", "end", values=(g, d["qtd"], f"{d['tempo']//60}h"))

        tree.pack(pady=5)


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
        self.top.geometry("850x650")
        centralizar_janela(self.top, 850, 650)

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
            self.top, text="Salvar (Recorte Automático Centro)", command=self._salvar
        )
        estilizar_botao(btn, "#27AE60")
        btn.pack(pady=10)

    def _salvar(self):
        target = self.img_orig.resize((600, 400), Image.LANCZOS)

        os.makedirs(os.path.dirname(WALLPAPER_PATH), exist_ok=True)
        target.save(WALLPAPER_PATH, "PNG")

        messagebox.showinfo("Sucesso", "Wallpaper atualizado!")
        self.callback()
        self.top.destroy()
