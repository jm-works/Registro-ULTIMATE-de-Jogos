import tkinter as tk


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
