import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import webbrowser
import urllib.parse
import re
import pyperclip
from PIL import Image, ImageTk
import os
import sys
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
from src.gui.componentes import estilizar_botao, CalendarioPicker
from src.gui.janelas import (
    JanelaChecklist,
    JanelaResumo,
    JanelaWallpaper,
    JanelaSeletorGenero,
    JanelaSeletorPlataforma,
    JanelaDetalhes,
    JanelaEditorDescricao,
)

# Definição da Escala estilo MyAnimeList
ESCALA_NOTAS = [
    "10 - Obra-prima",
    "9 - Incrível",
    "8 - Muito Bom",
    "7 - Bom",
    "6 - Razoável",
    "5 - Médio",
    "4 - Ruim",
    "3 - Muito Ruim",
    "2 - Horrível",
    "1 - Pavoroso",
]


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro ULTIMATE de Jogos")

        self.LARGURA = 600
        self.ALTURA = 400
        self.root.geometry(f"{self.LARGURA}x{self.ALTURA}")
        self.root.resizable(False, False)

        self.dados = GerenciadorDados()
        self.estatisticas = GeradorGraficos()

        self.lista_jogos = self.dados.carregar_jogos()
        self.jogos_visualizados = self.lista_jogos.copy()

        self._inicializar_variaveis()
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
        self.var_desc.trace("w", self._atualizar_botao_desc)

        self.var_horas = tk.StringVar(value="0")
        self.var_minutos = tk.StringVar(value="00")

        self.var_nota = tk.StringVar()
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
                largura_alvo = self.LARGURA
                altura_alvo = self.ALTURA

                wall = Image.open(WALLPAPER_PATH).convert("RGBA")
                bg = Image.open(BACKGROUND_PATH).convert("RGBA")

                wall = wall.resize((largura_alvo, altura_alvo), Image.LANCZOS)
                bg = bg.resize((largura_alvo, altura_alvo), Image.LANCZOS)

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
            label="Busca Avançada", command=self._abrir_janela_filtro
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
        self.root.columnconfigure(2, weight=1)

        self._criar_campo(0, "Título*:", self.var_titulo)

        tk.Label(self.root, text="Gênero*:").grid(
            row=1, column=0, sticky="w", padx=10, pady=3
        )

        frame_genero = tk.Frame(self.root)
        frame_genero.grid(row=1, column=1, sticky="w", padx=10)

        self.entry_gen = tk.Entry(
            frame_genero,
            textvariable=self.var_genero,
            width=17,
            state="readonly",
            disabledbackground="white",
            disabledforeground="black",
        )
        self.entry_gen.pack(side="left")

        btn_lupa = tk.Button(
            frame_genero,
            text="🔍",
            command=self._abrir_seletor_genero,
            cursor="hand2",
            relief="raised",
            bg="#e0e0e0",
            height=1,
        )
        btn_lupa.pack(side="left", padx=(3, 0))

        tk.Label(self.root, text="Plataforma*:").grid(
            row=2, column=0, sticky="w", padx=10, pady=3
        )

        frame_plataforma = tk.Frame(self.root)
        frame_plataforma.grid(row=2, column=1, sticky="w", padx=10)

        self.entry_plat = tk.Entry(
            frame_plataforma,
            textvariable=self.var_plataforma,
            width=17,
            state="readonly",
            disabledbackground="white",
            disabledforeground="black",
        )
        self.entry_plat.pack(side="left")

        btn_lupa_plat = tk.Button(
            frame_plataforma,
            text="🔍",
            command=self._abrir_seletor_plataforma,
            cursor="hand2",
            relief="raised",
            bg="#e0e0e0",
            height=1,
        )
        btn_lupa_plat.pack(side="left", padx=(3, 0))

        tk.Label(self.root, text="Data Zeramento:").grid(
            row=3, column=0, sticky="w", padx=10, pady=3
        )
        frame_data = tk.Frame(self.root)
        frame_data.grid(row=3, column=1, sticky="w", padx=10)

        entry_data = tk.Entry(frame_data, textvariable=self.var_data, width=15)
        entry_data.pack(side="left")

        btn_cal = tk.Button(
            frame_data,
            text="📅",
            command=lambda: CalendarioPicker(self.root, lambda d: self.var_data.set(d)),
            cursor="hand2",
            relief="flat",
            bg="#ddd",
            font=("Arial", 8),
        )
        btn_cal.pack(side="left", padx=2)

        self.var_data.trace_add("write", self._formatar_data)

        tk.Label(self.root, text="Estado*:").grid(
            row=4, column=0, sticky="w", padx=10, pady=3
        )
        cb_forma = ttk.Combobox(
            self.root,
            textvariable=self.var_forma,
            values=["História", "100%", "Platina", "Planejo Jogar", "Desistência"],
            state="readonly",
            width=18,
        )
        cb_forma.grid(row=4, column=1, sticky="w", padx=10)
        cb_forma.bind("<<ComboboxSelected>>", self._atualizar_campos_estado)

        tk.Label(self.root, text="Descrição:").grid(
            row=5, column=0, sticky="w", padx=10, pady=3
        )
        self.btn_editor = tk.Button(
            self.root,
            text="📝 Abrir Editor / Notas",
            command=self._abrir_editor_descricao,
            cursor="hand2",
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="raised",
            width=25,
        )
        self.btn_editor.grid(row=5, column=1, sticky="w", padx=10)

        tk.Label(self.root, text="Tempo Jogado:").grid(
            row=6, column=0, sticky="w", padx=10, pady=3
        )

        frame_tempo = tk.Frame(self.root)
        frame_tempo.grid(row=6, column=1, sticky="w", padx=10)

        vcmd_horas = (self.root.register(self._validar_input_horas), "%P")
        vcmd_minutos = (self.root.register(self._validar_input_minutos), "%P")

        self.spin_horas = tk.Spinbox(
            frame_tempo,
            from_=0,
            to=9999,
            textvariable=self.var_horas,
            width=5,
            font=("Arial", 10),
            wrap=False,
            validate="key",
            validatecommand=vcmd_horas,
        )
        self.spin_horas.pack(side="left")
        tk.Label(frame_tempo, text="h").pack(side="left", padx=(2, 8))

        self.spin_minutos = tk.Spinbox(
            frame_tempo,
            from_=0,
            to=59,
            textvariable=self.var_minutos,
            width=3,
            format="%02.0f",
            font=("Arial", 10),
            wrap=True,
            validate="key",
            validatecommand=vcmd_minutos,
        )
        self.spin_minutos.pack(side="left")
        tk.Label(frame_tempo, text="m").pack(side="left")

        tk.Label(self.root, text="Nota:").grid(
            row=7, column=0, sticky="w", padx=10, pady=3
        )

        self.cb_nota = ttk.Combobox(
            self.root,
            textvariable=self.var_nota,
            values=ESCALA_NOTAS,
            state="readonly",
            width=22,
        )
        self.cb_nota.grid(row=7, column=1, sticky="w", padx=10)

        btn_add = tk.Button(
            self.root, text="Adicionar Jogo", command=self.adicionar_jogo
        )
        estilizar_botao(btn_add, "gray", largura=15, altura=1)
        btn_add.place(x=90, y=280)

        frame_lista = tk.Frame(self.root)
        frame_lista.grid(row=0, column=4, rowspan=9, padx=12, pady=5, sticky="n")

        self.listbox = tk.Listbox(frame_lista, width=40, height=15)
        self.listbox.pack(side="left")

        sb = tk.Scrollbar(frame_lista, command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        self.listbox.bind("<Double-Button-1>", self.mostrar_info_jogo)
        self.listbox.bind("<Button-3>", self._abrir_menu_contexto)

    def _criar_campo(self, row, texto, variavel):
        tk.Label(self.root, text=texto).grid(
            row=row, column=0, sticky="w", padx=10, pady=3
        )
        entry = tk.Entry(self.root, textvariable=variavel, width=21)
        entry.grid(row=row, column=1, sticky="w", padx=10)
        return entry

    def _abrir_seletor_genero(self):
        def callback(selecionado):
            self.entry_gen.config(state="normal")
            self.var_genero.set(selecionado)
            self.entry_gen.config(state="readonly")

        JanelaSeletorGenero(self.root, callback)

    def _abrir_seletor_plataforma(self):
        def callback(selecionado):
            self.entry_plat.config(state="normal")
            self.var_plataforma.set(selecionado)
            self.entry_plat.config(state="readonly")

        JanelaSeletorPlataforma(self.root, callback)

    def _abrir_editor_descricao(self):
        def callback(texto):
            self.var_desc.set(texto)

        JanelaEditorDescricao(self.root, self.var_desc.get(), callback)

    def _atualizar_botao_desc(self, *args):
        texto = self.var_desc.get().strip()
        if texto:
            self.btn_editor.config(
                text="📝 Editar Descrição (Preenchido)", bg="#27AE60"
            )
        else:
            self.btn_editor.config(text="📝 Abrir Editor / Notas", bg="#3498db")

    def _validar_input_horas(self, valor):
        if valor == "":
            return True
        if not valor.isdigit():
            return False
        if len(valor) > 4:
            return False
        return int(valor) <= 9999

    def _validar_input_minutos(self, valor):
        if valor == "":
            return True
        if not valor.isdigit():
            return False
        return int(valor) <= 59

    def _filtrar_generos(self, event):
        pass

    def adicionar_jogo(self):
        tempo_str = ""
        if self.var_forma.get() not in ["Planejo Jogar", "Desistência"]:
            h = self.var_horas.get()
            m = self.var_minutos.get()
            if not h:
                h = "0"
            if not m:
                m = "00"
            tempo_str = f"{h}h {m.zfill(2)}m"

        nota_str = self.var_nota.get()
        nota_salvar = ""
        if nota_str:
            parts = nota_str.split(" - ")
            if len(parts) > 0:
                nota_salvar = parts[0]
        erro = validar_campos(
            self.var_titulo.get(),
            self.var_genero.get(),
            self.var_plataforma.get(),
            self.var_data.get(),
            tempo_str,
            nota_salvar if nota_salvar else 0,
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
            "Tempo Jogado": tempo_str,
            "Nota": (
                nota_salvar
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
            elif estado == "Platina":
                icone = "🏆"

            destaque = "💎 " if jogo.get("Hidden Gem") else ""
            self.listbox.insert(tk.END, f"{idx}. {icone} {destaque}{jogo['Título']}")

    def mostrar_info_jogo(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]
        JanelaDetalhes(self.root, jogo)

    def _abrir_menu_contexto(self, event):
        try:
            index = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)

            jogo_sel = self.jogos_visualizados[index]
            texto_gem = (
                "Remover 'Hidden Gem'"
                if jogo_sel.get("Hidden Gem")
                else "Marcar como 'Hidden Gem' 💎"
            )

            m = Menu(self.root, tearoff=0)

            m.add_command(
                label="📜 Ver Detalhes", command=lambda: self.mostrar_info_jogo(None)
            )
            m.add_separator()

            menu_org = Menu(m, tearoff=0)
            menu_org.add_command(
                label="Título (A-Z)", command=lambda: self._ordenar("titulo")
            )
            menu_org.add_command(
                label="Nota (Maior-Menor)", command=lambda: self._ordenar("nota")
            )
            menu_org.add_command(
                label="Data (Recente)", command=lambda: self._ordenar("data")
            )
            m.add_cascade(label="Organizar", menu=menu_org)
            m.add_separator()
            m.add_command(label=texto_gem, command=self._toggle_hidden_gem)
            m.add_separator()
            m.add_command(label="Copiar Nome", command=self._copiar_nome)
            m.add_command(label="Google", command=self._pesquisar_google)
            m.add_separator()
            m.add_command(label="Editar", command=self._editar_jogo_selecionado)
            m.add_command(label="Excluir", command=self._excluir_jogo_selecionado)
            m.post(event.x_root, event.y_root)
        except Exception:
            pass

    def _toggle_hidden_gem(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]
        jogo["Hidden Gem"] = not jogo.get("Hidden Gem", False)
        self.atualizar_lista_visual()

    def _ordenar(self, criterio):
        if criterio == "titulo":
            self.lista_jogos.sort(key=lambda x: x["Título"].lower())
        elif criterio == "nota":
            self.lista_jogos.sort(
                key=lambda x: float(x["Nota"]) if x["Nota"] else 0, reverse=True
            )
        elif criterio == "data":
            self.lista_jogos.sort(
                key=lambda x: (
                    datetime.strptime(x["Data de Zeramento"], "%d/%m/%Y")
                    if x.get("Data de Zeramento")
                    else datetime.min
                ),
                reverse=True,
            )
        self._limpar_filtros()

    def _copiar_nome(self):
        sel = self.listbox.curselection()
        if sel:
            pyperclip.copy(self.jogos_visualizados[sel[0]]["Título"])

    def _pesquisar_google(self):
        sel = self.listbox.curselection()
        if sel:
            webbrowser.open(
                f"https://www.google.com/search?q={urllib.parse.quote(self.jogos_visualizados[sel[0]]['Título'])}"
            )

    def _excluir_jogo_selecionado(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]
        if messagebox.askyesno("Excluir", f"Apagar '{jogo['Título']}'?"):
            self.lista_jogos.remove(jogo)
            self._limpar_filtros()

    def _editar_jogo_selecionado(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        jogo = self.jogos_visualizados[sel[0]]
        if jogo in self.lista_jogos:
            if messagebox.askyesno(
                "Editar", "Editar este jogo? (Volta para o formulário)"
            ):
                self.var_titulo.set(jogo["Título"])
                self.entry_gen.config(state="normal")
                self.var_genero.set(jogo["Gênero"])
                self.entry_gen.config(state="readonly")

                self.entry_plat.config(state="normal")
                self.var_plataforma.set(jogo["Plataforma"])
                self.entry_plat.config(state="readonly")

                self.var_data.set(jogo.get("Data de Zeramento", ""))
                self.var_forma.set(jogo["Forma de Zeramento"])
                self.var_desc.set(jogo.get("Descrição de Zeramento", ""))

                tempo = jogo.get("Tempo Jogado", "")
                h_val = "0"
                m_val = "00"
                if "h" in tempo:
                    try:
                        partes = tempo.split("h")
                        h_val = partes[0].strip()
                        if len(partes) > 1 and "m" in partes[1]:
                            m_val = partes[1].replace("m", "").strip()
                    except:
                        pass

                self.var_horas.set(h_val)
                self.var_minutos.set(m_val)

                nota_salva = str(jogo.get("Nota", "")).replace(".0", "")
                valor_combo = ""
                if nota_salva:
                    for item in ESCALA_NOTAS:
                        if item.startswith(f"{nota_salva} -"):
                            valor_combo = item
                            break
                    if not valor_combo:
                        try:
                            nota_int = int(float(nota_salva))
                            for item in ESCALA_NOTAS:
                                if item.startswith(f"{nota_int} -"):
                                    valor_combo = item
                                    break
                        except:
                            pass

                self.var_nota.set(valor_combo)

                self._atualizar_campos_estado()
                self.lista_jogos.remove(jogo)
                self._limpar_filtros()

    def _abrir_janela_filtro(self):
        top = tk.Toplevel(self.root)
        top.title("Busca Avançada")
        centralizar_janela(top, 350, 300)
        top.configure(padx=15, pady=15)

        tk.Label(top, text="Título:").pack(anchor="w")
        ent_titulo = tk.Entry(top)
        ent_titulo.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="Gênero:").pack(anchor="w")
        cb_gen = ttk.Combobox(top, values=[""] + GENEROS, state="readonly")
        cb_gen.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="Plataforma:").pack(anchor="w")
        cb_plat = ttk.Combobox(top, values=[""] + PLATAFORMAS, state="readonly")
        cb_plat.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="Estado:").pack(anchor="w")
        cb_est = ttk.Combobox(
            top,
            values=["", "História", "100%", "Platina", "Planejo Jogar", "Desistência"],
            state="readonly",
        )
        cb_est.pack(fill="x", pady=(0, 15))

        def aplicar():
            f_titulo = ent_titulo.get().lower()
            f_genero = cb_gen.get()
            f_plat = cb_plat.get()
            f_estado = cb_est.get()

            resultado = []
            for j in self.lista_jogos:
                match = True
                if f_titulo and f_titulo not in j["Título"].lower():
                    match = False
                if f_genero and f_genero != j["Gênero"]:
                    match = False
                if f_plat and f_plat != j["Plataforma"]:
                    match = False
                if f_estado and f_estado != j["Forma de Zeramento"]:
                    match = False

                if match:
                    resultado.append(j)

            self.jogos_visualizados = resultado
            self.atualizar_lista_visual()
            top.destroy()

        btn_aplicar = tk.Button(
            top,
            text="Aplicar Filtros",
            command=aplicar,
            bg="#4a90e2",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
        )
        btn_aplicar.pack(fill="x", pady=5)

    def _limpar_filtros(self):
        self.jogos_visualizados = self.lista_jogos.copy()
        self.atualizar_lista_visual()

    def _atualizar_campos_estado(self, event=None):
        if self.var_forma.get() in ["Planejo Jogar", "Desistência"]:
            self.var_horas.set("0")
            self.var_minutos.set("00")
            self.spin_horas.config(state="disabled")
            self.spin_minutos.config(state="disabled")

            self.var_data.set("")
            self.cb_nota.config(state="disabled")
        else:
            self.spin_horas.config(state="normal")
            self.spin_minutos.config(state="normal")
            self.cb_nota.config(state="readonly")
            if not self.var_data.get():
                self.var_data.set(datetime.now().strftime("%d/%m/%Y"))

    def _formatar_data(self, *args):
        t = "".join(filter(str.isdigit, self.var_data.get()))
        novo = t
        if len(t) > 2:
            novo = f"{t[:2]}/{t[2:]}"
        if len(t) > 4:
            novo = f"{t[:2]}/{t[2:4]}/{t[4:8]}"
        if len(novo) > 10:
            novo = novo[:10]
        if self.var_data.get() != novo:
            self.var_data.set(novo)

    def _limpar_campos(self):
        self.var_titulo.set("")

        self.entry_gen.config(state="normal")
        self.var_genero.set("")
        self.entry_gen.config(state="readonly")

        self.entry_plat.config(state="normal")
        self.var_plataforma.set("")
        self.entry_plat.config(state="readonly")

        self.var_desc.set("")

        self.var_horas.set("0")
        self.var_minutos.set("00")

        self.var_data.set("")
        self.var_nota.set("")

    def _exportar(self, tipo):
        c = filedialog.asksaveasfilename(defaultextension=f".{tipo}")
        if c:
            if tipo == "pdf":
                Exportador.exportar_pdf(self.lista_jogos, c)
            else:
                Exportador.exportar_excel(self.lista_jogos, c)
            messagebox.showinfo("Sucesso", "Exportado!")

    def _importar_excel(self):
        c = filedialog.askopenfilename()
        if c:
            n = Exportador.importar_excel(c)
            if n:
                self.lista_jogos.extend(n)
                self._limpar_filtros()
                messagebox.showinfo("Sucesso", "Importado!")

    def _resetar_dados(self):
        if messagebox.askyesno("Cuidado", "Apagar TUDO?"):
            self.dados.resetar_tudo()
            self.lista_jogos = []
            self._limpar_filtros()

    def ao_fechar(self):
        if messagebox.askyesno("Sair", "Salvar antes de sair?"):
            self.dados.salvar_jogos(self.lista_jogos)

        self.root.quit()
        self.root.destroy()
        os._exit(0)
