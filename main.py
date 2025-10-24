import tkinter as tk
from tkinter import messagebox
import db  # Importa o nosso arquivo db.py

# IMPORTA AS NOSSAS VIEWS
from views.clientes_view import ClientesView
from views.pedidos_view import PedidosView  # <-- ADICIONE ESTA LINHA


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Clientes & Pedidos")
        self.root.geometry("800x600")

        self.criar_menu_principal()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.label_inicio = tk.Label(self.main_frame,
                                     text="Bem-vindo!\nSelecione uma opção no menu.",
                                     font=("Arial", 16),
                                     bg="#f0f0f0")
        self.label_inicio.pack(pady=100)

    def criar_menu_principal(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        cadastro_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cadastros", menu=cadastro_menu)

        cadastro_menu.add_command(label="Clientes", command=self.abrir_tela_clientes)
        cadastro_menu.add_command(label="Pedidos", command=self.abrir_tela_pedidos)  # Este comando já existia
        cadastro_menu.add_separator()
        cadastro_menu.add_command(label="Sair", command=self.root.quit)

    def limpar_frame_principal(self):
        """Remove todos os widgets do frame principal antes de carregar uma nova tela."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def abrir_tela_clientes(self):
        self.limpar_frame_principal()
        ClientesView(self.main_frame)

    def abrir_tela_pedidos(self):
        # --- ESTA É A PARTE ATUALIZADA ---
        self.limpar_frame_principal()

        # Cria uma instância da nossa tela de pedidos
        # e a coloca dentro do frame principal
        PedidosView(self.main_frame)


# --- Ponto de entrada da aplicação ---
if __name__ == "__main__":
    # 1. Tenta inicializar o banco de dados
    try:
        db.inicializar_banco()
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Não foi possível inicializar o banco de dados: {e}")
        exit()  # Fecha o app se o banco falhar

    # 2. Se o banco estiver OK, inicia a aplicação Tkinter
    root = tk.Tk()
    app = App(root)
    root.mainloop()