import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date


def estilizar_botao(
    botao,
    cor_fundo,
    cor_texto="white",
    fonte=("Arial", 10, "bold"),
    largura=20,
    altura=2,
    wrap=150,
    borda=3,
    efeito_hover="#333333",
):
    botao.config(
        bg=cor_fundo,
        fg=cor_texto,
        font=fonte,
        width=largura,
        height=altura,
        wraplength=wrap,
        relief="raised",
        bd=borda,
        cursor="hand2",
    )

    botao.bind("<Enter>", lambda e: botao.config(bg=efeito_hover))
    botao.bind("<Leave>", lambda e: botao.config(bg=cor_fundo))


class CalendarioPicker(tk.Toplevel):
    def __init__(self, parent, callback_funcao):
        super().__init__(parent)
        self.callback = callback_funcao
        self.title("Escolher Data")
        self.geometry("300x280")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        # Centraliza no pai
        x = parent.winfo_rootx() + 50
        y = parent.winfo_rooty() + 50
        self.geometry(f"+{x}+{y}")

        self.ano_atual = date.today().year
        self.mes_atual = date.today().month
        self.selecionado = None

        self._criar_widgets()
        self.grab_set()

    def _criar_widgets(self):
        frame_top = tk.Frame(self, bg="#1e1e1e", pady=10)
        frame_top.pack(fill="x")

        btn_prev = tk.Button(
            frame_top,
            text="<",
            command=self._mes_anterior,
            bg="#333",
            fg="white",
            relief="flat",
        )
        btn_prev.pack(side="left", padx=15)

        self.lbl_mes_ano = tk.Label(
            frame_top, text="", font=("Arial", 12, "bold"), bg="#1e1e1e", fg="white"
        )
        self.lbl_mes_ano.pack(side="left", expand=True)

        btn_next = tk.Button(
            frame_top,
            text=">",
            command=self._mes_proximo,
            bg="#333",
            fg="white",
            relief="flat",
        )
        btn_next.pack(side="right", padx=15)
        frame_dias = tk.Frame(self, bg="#1e1e1e")
        frame_dias.pack(fill="x", padx=10)
        dias = ["D", "S", "T", "Q", "Q", "S", "S"]
        for i, d in enumerate(dias):
            tk.Label(frame_dias, text=d, width=5, bg="#1e1e1e", fg="#aaaaaa").grid(
                row=0, column=i
            )

        self.frame_grade = tk.Frame(self, bg="#1e1e1e")
        self.frame_grade.pack(fill="both", expand=True, padx=10, pady=5)

        self._atualizar_calendario()

    def _atualizar_calendario(self):
        for widget in self.frame_grade.winfo_children():
            widget.destroy()

        self.lbl_mes_ano.config(
            text=f"{calendar.month_name[self.mes_atual]} {self.ano_atual}"
        )

        cal = calendar.monthcalendar(self.ano_atual, self.mes_atual)

        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia != 0:
                    btn = tk.Button(
                        self.frame_grade,
                        text=str(dia),
                        width=4,
                        bg="#2d2d2d",
                        fg="white",
                        relief="flat",
                        command=lambda d=dia: self._selecionar(d),
                    )
                    if (
                        dia == date.today().day
                        and self.mes_atual == date.today().month
                        and self.ano_atual == date.today().year
                    ):
                        btn.config(bg="#4a90e2", font=("Arial", 9, "bold"))

                    btn.grid(row=r, column=c, padx=1, pady=1)

    def _mes_anterior(self):
        self.mes_atual -= 1
        if self.mes_atual < 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        self._atualizar_calendario()

    def _mes_proximo(self):
        self.mes_atual += 1
        if self.mes_atual > 12:
            self.mes_atual = 1
            self.ano_atual += 1
        self._atualizar_calendario()

    def _selecionar(self, dia):
        data_formatada = f"{dia:02d}/{self.mes_atual:02d}/{self.ano_atual}"
        self.callback(data_formatada)
        self.destroy()
