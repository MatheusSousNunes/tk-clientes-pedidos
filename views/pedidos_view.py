import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import db  # Importa nosso arquivo db.py


class PedidosView(tk.Frame):
    """
    Tela de Gerenciamento de Pedidos (Lista).
    Este Frame é carregado dentro da janela principal.
    """

    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.criar_widgets_botoes()
        self.criar_treeview_pedidos()

        self.recarregar_lista_pedidos()

    def criar_widgets_botoes(self):
        frame_botoes = tk.Frame(self, bg="#f0f0f0")
        frame_botoes.pack(fill=tk.X, pady=5)

        btn_novo = tk.Button(frame_botoes, text="Novo Pedido", command=self.abrir_formulario_novo)
        btn_novo.pack(side=tk.LEFT, padx=5)

    def criar_treeview_pedidos(self):
        frame_lista = tk.Frame(self)
        frame_lista.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_pedidos = ttk.Treeview(
            frame_lista,
            columns=("ID", "Cliente", "Data", "Total"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree_pedidos.yview)

        self.tree_pedidos.heading("ID", text="ID Pedido")
        self.tree_pedidos.heading("Cliente", text="Cliente")
        self.tree_pedidos.heading("Data", text="Data")
        self.tree_pedidos.heading("Total", text="Total (R$)")

        self.tree_pedidos.column("ID", width=80, stretch=tk.NO)
        self.tree_pedidos.column("Cliente", width=250)
        self.tree_pedidos.column("Data", width=100)
        self.tree_pedidos.column("Total", width=100, anchor=tk.E)

        self.tree_pedidos.pack(fill=tk.BOTH, expand=True)

        # CORREÇÃO: Removidas as funções 'on_closing' e 'carregar_clientes'
        # que estavam coladas aqui por engano.

    def recarregar_lista_pedidos(self):
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)

        # Query com JOIN para pegar o nome do cliente
        query = """
            SELECT p.id, c.nome, p.data, p.total 
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.data DESC
        """
        pedidos = db.executar_select(query)

        for pedido in pedidos:
            total_formatado = f"{pedido['total']:.2f}"
            self.tree_pedidos.insert("", tk.END, values=(pedido['id'], pedido['nome'], pedido['data'], total_formatado))

    def abrir_formulario_novo(self):
        # Abre o formulário de pedido
        FormularioPedido(self.master, callback_sucesso=self.recarregar_lista_pedidos)


# --- FIM DA CLASSE PedidosView ---


class FormularioPedido(tk.Toplevel):
    """
    Formulário Tkinter (janela Toplevel) para criar Pedido.
    Baseado no Prompt 4.
    """

    def __init__(self, parent, callback_sucesso):
        super().__init__(parent)

        self.title("Criar Novo Pedido")
        self.callback_sucesso = callback_sucesso
        self.clientes_map = {}  # Dicionário para { "Nome (ID)": id }
        self.itens_no_carrinho = []  # Lista de dicionários

        self.transient(parent)
        self.grab_set()

        self.criar_formulario()
        self.carregar_clientes()
        self.atualizar_total()  # Inicia o total como 0.00

        # Prompt 5: Prevenção de fechar janela
        # CORREÇÃO: Removida a linha duplicada de self.atualizar_total()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # CORREÇÃO: O método 'on_closing' foi movido para aqui,
    # no nível da classe FormularioPedido (mesma indentação de '__init__')
    def on_closing(self):
        """ Prompt 5: Prevenção de fechar janela com dados não salvos """
        # Apenas pergunta se houver itens no carrinho, senão só fecha
        if self.itens_no_carrinho:
            if messagebox.askyesno("Sair sem Salvar?",
                                   "Você tem itens no pedido.\nTem certeza que quer fechar? O pedido não será salvo."):
                self.destroy()
        else:
            self.destroy()  # Fecha direto se o carrinho estiver vazio

    def criar_formulario(self):
        # Frame principal
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção 1: Cliente e Data ---
        frame_info = tk.Frame(main_frame)
        frame_info.pack(fill=tk.X)

        tk.Label(frame_info, text="Cliente:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_clientes = ttk.Combobox(frame_info, state="readonly", width=40)
        self.combo_clientes.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(frame_info, text="Data:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_data = tk.Entry(frame_info, width=12)
        self.entry_data.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        # "campo Data (hoje por padrão)"
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # --- Seção 2: Adicionar Itens ---
        frame_add_item = ttk.LabelFrame(main_frame, text="Adicionar Item", padding=10)
        frame_add_item.pack(fill=tk.X, pady=10)

        tk.Label(frame_add_item, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_produto = tk.Entry(frame_add_item, width=30)
        self.entry_produto.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_add_item, text="Qtd:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_qtd = tk.Entry(frame_add_item, width=5)
        self.entry_qtd.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_add_item, text="Preço Unit:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_preco = tk.Entry(frame_add_item, width=8)
        self.entry_preco.grid(row=0, column=5, padx=5, pady=5)

        # "botões Adicionar/Remover item"
        btn_add = tk.Button(frame_add_item, text="Adicionar", command=self.adicionar_item)
        btn_add.grid(row=0, column=6, padx=10, pady=5)

        # --- Seção 3: Tabela de Itens (Treeview) ---
        # "tabela de itens (produto/quantidade/preço)"
        frame_itens_tabela = ttk.Frame(main_frame)
        frame_itens_tabela.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree_itens = ttk.Treeview(
            frame_itens_tabela,
            columns=("Produto", "Qtd", "Preço Unit", "Subtotal"),
            show="headings"
        )
        self.tree_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para a tabela de itens
        scrollbar_itens = tk.Scrollbar(frame_itens_tabela, orient="vertical", command=self.tree_itens.yview)
        scrollbar_itens.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_itens.configure(yscrollcommand=scrollbar_itens.set)

        self.tree_itens.heading("Produto", text="Produto")
        self.tree_itens.heading("Qtd", text="Qtd")
        self.tree_itens.heading("Preço Unit", text="Preço Unit.")
        self.tree_itens.heading("Subtotal", text="Subtotal")

        self.tree_itens.column("Produto", width=200)
        self.tree_itens.column("Qtd", width=50, anchor=tk.CENTER)
        self.tree_itens.column("Preço Unit", width=80, anchor=tk.E)
        self.tree_itens.column("Subtotal", width=80, anchor=tk.E)

        # --- Seção 4: Total e Botões de Ação ---
        frame_final = tk.Frame(main_frame)
        frame_final.pack(fill=tk.X, pady=10)

        btn_remover = tk.Button(frame_final, text="Remover Item Selecionado", command=self.remover_item)
        btn_remover.pack(side=tk.LEFT, padx=5)

        self.label_total = tk.Label(frame_final, text="Total: R$ 0.00", font=("Arial", 14, "bold"))
        self.label_total.pack(side=tk.RIGHT, padx=10)

        # Botões Salvar/Cancelar
        frame_botoes = tk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=10)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Pedido", command=self.salvar_pedido,
                               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
        btn_salvar.pack(side=tk.RIGHT, padx=5)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

    def carregar_clientes(self):
        """ "selecione Cliente (Combobox)"  """
        clientes = db.executar_select("SELECT id, nome FROM clientes ORDER BY nome")
        opcoes_combobox = []

        for cliente in clientes:
            texto_opcao = f"{cliente['nome']} (ID: {cliente['id']})"
            opcoes_combobox.append(texto_opcao)
            # Mapeia o texto de volta para o ID
            self.clientes_map[texto_opcao] = cliente['id']

        self.combo_clientes['values'] = opcoes_combobox
        if opcoes_combobox:
            self.combo_clientes.current(0)  # Seleciona o primeiro

    def adicionar_item(self):
        produto = self.entry_produto.get()
        try:
            quantidade = int(self.entry_qtd.get())
            preco_unit = float(self.entry_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Erro de Formato",
                                   "Quantidade deve ser um número inteiro e Preço deve ser um número (ex: 12.50).")
            return

        if not produto or quantidade <= 0 or preco_unit <= 0:
            messagebox.showwarning("Validação", "Preencha todos os campos do item (Produto, Qtd > 0, Preço > 0).")
            return

        subtotal = quantidade * preco_unit

        # Adiciona na Treeview
        valores = (produto, quantidade, f"{preco_unit:.2f}", f"{subtotal:.2f}")
        item_id = self.tree_itens.insert("", tk.END, values=valores)

        # Adiciona na lista interna para salvar no DB (e para remoção)
        self.itens_no_carrinho.append({
            "id_treeview": item_id,
            "produto": produto,
            "quantidade": quantidade,
            "preco_unit": preco_unit
        })

        # Limpa os campos de entrada
        self.entry_produto.delete(0, tk.END)
        self.entry_qtd.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.entry_produto.focus()

        self.atualizar_total()

    def remover_item(self):
        selecionado = self.tree_itens.focus()
        if not selecionado:
            messagebox.showwarning("Remover Item", "Selecione um item na lista para remover.")
            return

        # Remove da lista interna
        # Encontra o item na lista interna pelo seu 'id_treeview'
        item_para_remover = None
        for item in self.itens_no_carrinho:
            if item["id_treeview"] == selecionado:
                item_para_remover = item
                break

        if item_para_remover:
            self.itens_no_carrinho.remove(item_para_remover)

        # Remove da Treeview
        self.tree_itens.delete(selecionado)

        self.atualizar_total()

    def atualizar_total(self):
        """ "cálculo automático do total"  """
        total = 0.0
        for item in self.itens_no_carrinho:
            total += item['quantidade'] * item['preco_unit']

        self.total_calculado = total  # Armazena para salvar
        self.label_total.config(text=f"Total: R$ {total:.2f}")

    def salvar_pedido(self):
        # 1. Validar dados do Pedido
        cliente_selecionado_texto = self.combo_clientes.get()
        if not cliente_selecionado_texto:
            messagebox.showwarning("Validação", "Selecione um cliente.")
            return

        if not self.itens_no_carrinho:
            messagebox.showwarning("Validação", "O pedido deve ter pelo menos um item.")
            return

        data_pedido = self.entry_data.get()
        # Validação simples da data
        try:
            datetime.strptime(data_pedido, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validação", "Formato da data inválido. Use AAAA-MM-DD.")
            return

        # 2. Pegar os dados para salvar
        cliente_id = self.clientes_map[cliente_selecionado_texto]
        total_final = self.total_calculado
        itens = self.itens_no_carrinho

        # 3. Chamar a função transacional do db.py
        pedido_id = db.salvar_pedido_e_itens(cliente_id, data_pedido, total_final, itens)

        if pedido_id:
            messagebox.showinfo("Sucesso", f"Pedido #{pedido_id} salvo com sucesso!")
            self.callback_sucesso()  # Recarrega a lista principal
            self.destroy()  # Fecha a janela
        else:
            messagebox.showerror("Erro de Banco de Dados", "Ocorreu um erro ao salvar o pedido. Verifique os logs.")