import tkinter as tk
from src.gui.app import App
from src.utils import centralizar_janela

if __name__ == "__main__":
    root = tk.Tk()

    app = App(root)

    centralizar_janela(root, 600, 400)

    root.mainloop()
