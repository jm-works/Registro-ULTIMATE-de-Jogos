import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import webbrowser
import urllib.parse
import re
import pyperclip
from PIL import Image, ImageTk
import os
from datetime import datetime

from src.constantes import (
    ASSETS_DIR,
    ICON_PATH,
    WALLPAPER_PATH,
    BACKGROUND_PATH,
    GENEROS,
    PLATAFORMAS,
)
from src.utils import centralizar_janela, validar_campos, calcular_total_minutos
from src.dados import GerenciadorDados
from src.estatisticas import GeradorGraficos
from src.exportacao import Exportador
from src.gui.componentes import estilizar_botao
from src.gui.janelas import JanelaChecklist, JanelaResumo, JanelaWallpaper


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro ULTIMATE de Jogos")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.dados = GerenciadorDados()
        self.estatisticas = GeradorGraficos()

        self.lista_jogos = self.dados.carregar_jogos()
        self.jogos_visualizados = self.lista_jogos.copy()

        self._inicializar_variaveis()

        # Configuração Visual
        self._carregar_assets()
        self._criar_menu()
        self._criar_widgets()

        self.atualizar_lista_visual()

        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def _inicializar_variaveis(self):
        self.var_titulo = tk.StringVar()
        self.var_genero = tk.StringVar()
        self.var_plataforma = tk.StringVar()
        self.var_data = tk.StringVar()
        self.var_forma = tk.StringVar()
        self.var_desc = tk.StringVar()
        self.var_tempo = tk.StringVar()
        self.var_nota = tk.DoubleVar(value=1.0)
        self.var_busca = tk.StringVar()

    def _carregar_assets(self):
        try:
            if os.path.exists(ICON_PATH):
                self.root.iconbitmap(ICON_PATH)

            self.atualizar_fundo()
        except Exception as e:
            print(f"Erro ao carregar assets: {e}")

    def atualizar_fundo(self):
        if os.path.exists(WALLPAPER_PATH) and os.path.exists(BACKGROUND_PATH):
            try:
                wall = Image.open(WALLPAPER_PATH).convert("RGBA")
                bg = Image.open(BACKGROUND_PATH).convert("RGBA")
                wall = wall.resize(bg.size)
                final = Image.alpha_composite(wall, bg)
                self.bg_tk = ImageTk.PhotoImage(final)

                if hasattr(self, "lbl_fundo"):
                    self.lbl_fundo.destroy()

                self.lbl_fundo = tk.Label(self.root, image=self.bg_tk)
                self.lbl_fundo.place(x=0, y=0, relwidth=1, relheight=1)
                self.lbl_fundo.lower()
            except Exception:
                pass

    def _criar_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(
            label="Exportar PDF", command=lambda: self._exportar("pdf")
        )
        file_menu.add_command(
            label="Exportar Excel", command=lambda: self._exportar("excel")
        )
        file_menu.add_command(label="Importar Excel", command=self._importar_excel)
        file_menu.add_separator()
        file_menu.add_command(
            label="Alterar Wallpaper",
            command=lambda: JanelaWallpaper(self.root, self.atualizar_fundo),
        )
        file_menu.add_command(label="Resetar Tudo", command=self._resetar_dados)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.ao_fechar)

        filter_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Filtro", menu=filter_menu)
        filter_menu.add_command(
            label="Filtrar Jogos", command=self._abrir_janela_filtro
        )
        filter_menu.add_command(label="Limpar Filtros", command=self._limpar_filtros)

        info_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Informações", menu=info_menu)
        info_menu.add_command(
            label="Jogos por Plataforma",
            command=lambda: self.estatisticas.criar_distribuicao_plataformas(
                self.lista_jogos
            ),
        )
        info_menu.add_command(
            label="Média de Notas",
            command=lambda: self.estatisticas.criar_media_notas_plataformas(
                self.lista_jogos
            ),
        )
        info_menu.add_command(
            label="Tempo Total Jogado",
            command=lambda: self.estatisticas.criar_tempo_total_plataformas(
                self.lista_jogos
            ),
        )
        info_menu.add_command(
            label="Jogos por Ano",
            command=lambda: self.estatisticas.criar_grafico_jogos_por_ano(
                self.lista_jogos
            ),
        )
        info_menu.add_command(
            label="Gêneros (Pizza)",
            command=lambda: self.estatisticas.criar_grafico_generos(self.lista_jogos),
        )
        info_menu.add_command(
            label="Análise de Notas",
            command=lambda: self.estatisticas.criar_analise_de_notas(self.lista_jogos),
        )

        menu_bar.add_command(
            label="Tarefas", command=lambda: JanelaChecklist(self.root, self.dados)
        )
        menu_bar.add_command(
            label="Resumo", command=lambda: JanelaResumo(self.root, self.lista_jogos)
        )

    def _criar_widgets(self):
        self._criar_campo(0, "Título*:", self.var_titulo)

        tk.Label(self.root, text="Gênero*:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        cb_gen = ttk.Combobox(
            self.root,
            textvariable=self.var_genero,
            values=GENEROS,
            state="readonly",
            width=17,
        )
        cb_gen.grid(row=1, column=1, sticky="w", padx=10)

        tk.Label(self.root, text="Plataforma*:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )
        cb_plat = ttk.Combobox(
            self.root, textvariable=self.var_plataforma, values=PLATAFORMAS, width=17
        )
        cb_plat.grid(row=2, column=1, sticky="w", padx=10)

        self._criar_campo(3, "Data Zeramento:", self.var_data)
        self.var_data.trace_add("write", self._formatar_data)  # Auto-formatação

        tk.Label(self.root, text="Estado*:").grid(
            row=4, column=0, sticky="w", padx=10, pady=5
        )
        cb_forma = ttk.Combobox(
            self.root,
            textvariable=self.var_forma,
            values=["História", "100%", "Platina", "Planejo Jogar", "Desistência"],
            state="readonly",
            width=17,
        )
        cb_forma.grid(row=4, column=1, sticky="w", padx=10)
        cb_forma.bind("<<ComboboxSelected>>", self._atualizar_campos_estado)

        self._criar_campo(5, "Descrição:", self.var_desc)

        self._criar_campo(6, "Tempo (HH:MM):", self.var_tempo)
        self.var_tempo.trace_add("write", self._formatar_tempo)

        tk.Label(self.root, text="Nota (1-10):").grid(
            row=7, column=0, sticky="w", padx=10, pady=5
        )
        self.slider_nota = tk.Scale(
            self.root, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.var_nota
        )
        self.slider_nota.grid(row=7, column=1, sticky="ew", padx=10)

        btn_add = tk.Button(
            self.root, text="Adicionar Jogo", command=self.adicionar_jogo
        )
        estilizar_botao(btn_add, "gray", largura=15, altura=1)
        btn_add.grid(row=8, column=0, columnspan=2, pady=10)

        frame_lista = tk.Frame(self.root)
        frame_lista.grid(row=0, column=2, rowspan=9, padx=10, pady=5, sticky="ns")

        self.listbox = tk.Listbox(frame_lista, width=40, height=18)
        self.listbox.pack(side="left", fill="both")
        sb = tk.Scrollbar(frame_lista, command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        self.listbox.bind("<Double-Button-1>", self.mostrar_info_jogo)
        self.listbox.bind("<Button-3>", self._abrir_menu_contexto)  # Botão direito

    def _criar_campo(self, row, texto, variavel):
        tk.Label(self.root, text=texto).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=variavel).grid(
            row=row, column=1, sticky="w", padx=10
        )

    def adicionar_jogo(self):
        erro = validar_campos(
            self.var_titulo.get(),
            self.var_genero.get(),
            self.var_plataforma.get(),
            self.var_data.get(),
            self.var_tempo.get(),
            self.var_nota.get(),
            self.var_forma.get(),
        )
        if erro:
            messagebox.showerror("Erro", erro)
            return

        novo_jogo = {
            "Título": self.var_titulo.get(),
            "Gênero": self.var_genero.get(),
            "Plataforma": self.var_plataforma.get(),
            "Data de Zeramento": (
                self.var_data.get()
                if self.var_forma.get() not in ["Planejo Jogar", "Desistência"]
                else ""
            ),
            "Forma de Zeramento": self.var_forma.get(),
            "Descrição de Zeramento": self.var_desc.get(),
            "Tempo Jogado": (
                self.var_tempo.get()
                if self.var_forma.get() not in ["Planejo Jogar", "Desistência"]
                else ""
            ),
            "Nota": (
                self.var_nota.get()
                if self.var_forma.get() not in ["Planejo Jogar", "Desistência"]
                else ""
            ),
        }

        self.lista_jogos.append(novo_jogo)
        self._limpar_filtros()
        self._limpar_campos()
        messagebox.showinfo("Sucesso", "Jogo adicionado!")

    def atualizar_lista_visual(self):
        self.listbox.delete(0, tk.END)
        for idx, jogo in enumerate(self.jogos_visualizados, 1):
            icone = "✅"
            estado = jogo.get("Forma de Zeramento")
            if estado == "Planejo Jogar":
                icone = "📅"
            elif estado == "Desistência":
                icone = "❌"

            self.listbox.insert(tk.END, f"{idx}. {icone} {jogo['Título']}")

    def mostrar_info_jogo(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]

        msg = (
            f"Título: {jogo['Título']}\n"
            f"Gênero: {jogo['Gênero']}\n"
            f"Plataforma: {jogo['Plataforma']}\n"
            f"Estado: {jogo['Forma de Zeramento']}\n"
            f"Tempo: {jogo.get('Tempo Jogado', 'N/A')}\n"
            f"Nota: {jogo.get('Nota', 'N/A')}"
        )
        messagebox.showinfo("Detalhes", msg)

    def _abrir_menu_contexto(self, event):
        try:
            index = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)

            m = Menu(self.root, tearoff=0)
            m.add_command(label="Pesquisar no Google", command=self._pesquisar_google)
            m.add_command(label="Editar", command=self._editar_jogo_selecionado)
            m.add_command(label="Excluir", command=self._excluir_jogo_selecionado)
            m.post(event.x_root, event.y_root)
        except Exception:
            pass

    def _pesquisar_google(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]
        webbrowser.open(
            f"https://www.google.com/search?q={urllib.parse.quote(jogo['Título'])}"
        )

    def _excluir_jogo_selecionado(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        jogo_visual = self.jogos_visualizados[sel[0]]
        if messagebox.askyesno("Excluir", f"Apagar '{jogo_visual['Título']}'?"):
            self.lista_jogos.remove(jogo_visual)
            self._limpar_filtros()
            messagebox.showinfo("Sucesso", "Jogo removido.")

    def _editar_jogo_selecionado(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]

        if messagebox.askyesno(
            "Editar",
            "Isso carregará os dados para o formulário e removerá o registro atual para que você salve novamente. Continuar?",
        ):
            self.var_titulo.set(jogo["Título"])
            self.var_genero.set(jogo["Gênero"])
            self.var_plataforma.set(jogo["Plataforma"])
            self.var_data.set(jogo.get("Data de Zeramento", ""))
            self.var_forma.set(jogo["Forma de Zeramento"])
            self.var_desc.set(jogo.get("Descrição de Zeramento", ""))
            self.var_tempo.set(jogo.get("Tempo Jogado", ""))
            try:
                self.var_nota.set(float(jogo["Nota"]))
            except:
                self.var_nota.set(1)

            self.lista_jogos.remove(jogo)
            self._limpar_filtros()

    def _abrir_janela_filtro(self):
        top = tk.Toplevel(self.root)
        top.title("Filtrar")
        centralizar_janela(top, 300, 150)

        tk.Label(top, text="Buscar por Título:").pack(pady=5)
        entry = tk.Entry(top)
        entry.pack(pady=5)

        def aplicar():
            termo = entry.get().lower()
            self.jogos_visualizados = [
                j for j in self.lista_jogos if termo in j["Título"].lower()
            ]
            self.atualizar_lista_visual()
            top.destroy()

        tk.Button(top, text="Filtrar", command=aplicar).pack(pady=10)

    def _limpar_filtros(self):
        self.jogos_visualizados = self.lista_jogos.copy()
        self.atualizar_lista_visual()

    def _atualizar_campos_estado(self, event=None):
        if self.var_forma.get() in ["Planejo Jogar", "Desistência"]:
            self.var_tempo.set("")
            self.var_data.set("")
            self.slider_nota.config(state="disabled")
        else:
            self.slider_nota.config(state="normal")

    def _formatar_data(self, *args):
        t = self.var_data.get()
        t = "".join(filter(str.isdigit, t))
        if len(t) > 8:
            t = t[:8]
        if len(t) >= 2:
            t = t[:2] + "/" + t[2:]
        if len(t) >= 5:
            t = t[:5] + "/" + t[5:]
        if self.var_data.get() != t:
            self.var_data.set(t)

    def _formatar_tempo(self, *args):
        t = self.var_tempo.get().replace(" ", "")
        pass

    def _limpar_campos(self):
        self.var_titulo.set("")
        self.var_genero.set("")
        self.var_plataforma.set("")
        self.var_desc.set("")
        self.var_tempo.set("")
        self.var_data.set("")
        self.var_nota.set(1)

    # --- Persistência ---
    def _exportar(self, tipo):
        caminho = filedialog.asksaveasfilename(defaultextension=f".{tipo}")
        if not caminho:
            return

        sucesso = False
        if tipo == "pdf":
            sucesso = Exportador.exportar_pdf(self.lista_jogos, caminho)
        else:
            sucesso = Exportador.exportar_excel(self.lista_jogos, caminho)

        if sucesso:
            messagebox.showinfo("Sucesso", "Exportação concluída!")

    def _importar_excel(self):
        caminho = filedialog.askopenfilename()
        if not caminho:
            return
        novos = Exportador.importar_excel(caminho)
        if novos:
            self.lista_jogos.extend(novos)
            self._limpar_filtros()
            messagebox.showinfo("Sucesso", f"{len(novos)} jogos importados!")

    def _resetar_dados(self):
        if messagebox.askyesno("Cuidado", "Isso apagará TUDO. Continuar?"):
            self.dados.resetar_tudo()
            self.lista_jogos = []
            self._limpar_filtros()

    def ao_fechar(self):
        if messagebox.askyesno("Sair", "Deseja salvar antes de sair?"):
            self.dados.salvar_jogos(self.lista_jogos)
        self.root.destroy()
