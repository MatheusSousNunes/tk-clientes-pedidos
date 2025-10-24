import tkinter as tk
from tkinter import ttk, messagebox
import re  # Para validar o email
import db  # Importa nosso arquivo db.py


class ClientesView(tk.Frame):
    """
    Tela de Gerenciamento de Clientes (Prompt 3: Lista e busca).
    Este Frame é carregado dentro da janela principal (no main_frame).
    """

    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.criar_widgets_busca_e_botoes()
        self.criar_treeview_lista()

        # Carrega os dados iniciais
        self.recarregar_lista_clientes()

    def criar_widgets_busca_e_botoes(self):
        # Frame para a busca e botões
        frame_controles = tk.Frame(self, bg="#f0f0f0")
        frame_controles.pack(fill=tk.X, pady=5)

        tk.Label(frame_controles, text="Buscar:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 5))

        self.entry_busca = tk.Entry(frame_controles, width=30)
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        btn_buscar = tk.Button(frame_controles, text="Buscar", command=self.buscar_cliente)
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Botões de Ação (Novo, Editar, Excluir)
        frame_botoes = tk.Frame(self, bg="#f0f0f0")
        frame_botoes.pack(fill=tk.X, pady=(5, 10))

        btn_novo = tk.Button(frame_botoes, text="Novo Cliente", command=self.abrir_formulario_novo)
        btn_novo.pack(side=tk.LEFT, padx=5)

        btn_editar = tk.Button(frame_botoes, text="Editar Selecionado", command=self.abrir_formulario_editar)
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_excluir = tk.Button(frame_botoes, text="Excluir Selecionado", command=self.excluir_cliente)
        btn_excluir.pack(side=tk.LEFT, padx=5)

    def criar_treeview_lista(self):
        # Frame para a lista (Treeview) com scrollbar
        frame_lista = tk.Frame(self)
        frame_lista.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            frame_lista,
            columns=("ID", "Nome", "Email", "Telefone"),
            show="headings",
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(command=self.tree.yview)

        # Definindo os cabeçalhos
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Telefone", text="Telefone")

        # Definindo a largura das colunas
        self.tree.column("ID", width=50, stretch=tk.NO)
        self.tree.column("Nome", width=200)
        self.tree.column("Email", width=250)
        self.tree.column("Telefone", width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def recarregar_lista_clientes(self, termo_busca=None):
        """
        Limpa e recarrega a Treeview com dados do banco.
        "Recarregue a lista após operações."
        """
        # Limpa a lista antiga
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Busca os dados no banco
        if termo_busca:
            # "barra de busca por nome/email"
            query = "SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ?"
            params = (f'%{termo_busca}%', f'%{termo_busca}%')
        else:
            query = "SELECT * FROM clientes ORDER BY nome"
            params = ()

        clientes = db.executar_select(query, params)

        # Insere os dados na lista
        for cliente in clientes:
            self.tree.insert("", tk.END, values=(cliente['id'], cliente['nome'], cliente['email'], cliente['telefone']))

    def buscar_cliente(self):
        termo = self.entry_busca.get()
        self.recarregar_lista_clientes(termo)

    def abrir_formulario_novo(self):
        # Abre o formulário em modo "novo"
        # O 'self' é passado para que o formulário possa chamar
        # o método 'recarregar_lista_clientes' quando terminar.
        FormularioCliente(self.master, modo="novo", callback_sucesso=self.recarregar_lista_clientes)

    def abrir_formulario_editar(self):
        # Pega o item selecionado na lista
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Editar Cliente", "Por favor, selecione um cliente na lista para editar.")
            return

        # Pega os dados do item selecionado
        dados_cliente = self.tree.item(selecionado, 'values')
        id_cliente = dados_cliente[0]

        # Abre o formulário em modo "editar" e passa o ID
        FormularioCliente(self.master, modo="editar", cliente_id=id_cliente,
                          callback_sucesso=self.recarregar_lista_clientes)

    def excluir_cliente(self):
        # Pega o item selecionado
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Excluir Cliente", "Por favor, selecione um cliente na lista para excluir.")
            return

        dados_cliente = self.tree.item(selecionado, 'values')
        id_cliente = dados_cliente[0]
        nome_cliente = dados_cliente[1]

        # "Ao excluir, peça confirmação."
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o cliente '{nome_cliente}'?"):
            try:
                # Tenta excluir pedidos associados primeiro (regra de negócio)
                db.executar_comando(
                    "DELETE FROM itens_pedido WHERE pedido_id IN (SELECT id FROM pedidos WHERE cliente_id = ?)",
                    (id_cliente,))
                db.executar_comando("DELETE FROM pedidos WHERE cliente_id = ?", (id_cliente,))
                # Exclui o cliente
                db.executar_comando("DELETE FROM clientes WHERE id = ?", (id_cliente,))

                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")
                self.recarregar_lista_clientes()  # Atualiza a lista
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir cliente: {e}")


# --- FIM DA CLASSE ClientesView ---


class FormularioCliente(tk.Toplevel):
    """
    Formulário Tkinter (janela Toplevel) para cadastrar/editar Clientes.
    Baseado no Prompt 2.
    """

    def __init__(self, parent, modo, callback_sucesso, cliente_id=None):
        super().__init__(parent)

        self.modo = modo
        self.cliente_id = cliente_id
        self.callback_sucesso = callback_sucesso  # Função para chamar após salvar

        if self.modo == "editar":
            self.title("Editar Cliente")
            self.carregar_dados_cliente()
        else:
            self.title("Novo Cliente")
            self.dados_cliente = None

        self.transient(parent)  # Mantém a janela na frente
        self.grab_set()  # Modal

        self.criar_formulario() # ESTA É A LINHA 183 DO TRACEBACK

        # Prompt 5: Prevenção de fechar janela
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def carregar_dados_cliente(self):
        dados = db.executar_select("SELECT * FROM clientes WHERE id = ?", (self.cliente_id,))
        if dados:
            self.dados_cliente = dados[0]
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do cliente.")
            self.destroy()

    def criar_formulario(self):
        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Dicionário para guardar as Entry widgets
        self.entries = {}

        # Lista de campos
        campos = ["Nome", "Email", "Telefone"]

        for i, campo in enumerate(campos):
            tk.Label(frame, text=f"{campo}:").grid(row=i, column=0, sticky=tk.W, pady=5)

            entry = tk.Entry(frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[campo] = entry

            # Preenche os campos se estiver no modo "editar"
            if self.dados_cliente:
                entry.insert(0, self.dados_cliente.get(campo.lower(), ""))

        # Botões Salvar/Cancelar
        frame_botoes = tk.Frame(frame)
        frame_botoes.grid(row=len(campos), column=0, columnspan=2, pady=10)

        btn_salvar = tk.Button(frame_botoes, text="Salvar", command=self.salvar) # ESTA É A LINHA 222
        btn_salvar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    # --- FIM DO MÉTODO criar_formulario ---

    def on_closing(self):
        """ Prompt 5: Prevenção de fechar janela com dados não salvos """
        # Pergunta ao usuário se ele realmente quer fechar
        if messagebox.askyesno("Sair sem Salvar?",
                               "Tem certeza que quer fechar?\nQualquer alteração não salva será perdida."):
            self.destroy()  # Fecha a janela se o usuário confirmar

    def validar_dados(self):
        """
        Valida os campos do formulário.
        """
        nome = self.entries["Nome"].get()
        email = self.entries["Email"].get()
        telefone = self.entries["Telefone"].get()

        # "Valide: nome obrigatório"
        if not nome:
            messagebox.showwarning("Validação", "O campo 'Nome' é obrigatório.")
            return False

        # "e-mail em formato simples"
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showwarning("Validação", "O formato do 'Email' é inválido.")
            return False

        # "telefone com 8-15 dígitos" (apenas números)
        telefone_digitos = re.sub(r'\D', '', telefone)  # Remove não-dígitos
        if telefone and not (8 <= len(telefone_digitos) <= 15):
            messagebox.showwarning("Validação", "O 'Telefone' deve conter entre 8 e 15 dígitos.")
            return False

        return True

    def salvar(self):
        """
        Callback do botão Salvar.
        Valida e salva no banco de dados.
        """
        if not self.validar_dados():
            return  # Para a execução se a validação falhar

        # Pega os dados validados
        nome = self.entries["Nome"].get()
        email = self.entries["Email"].get()
        telefone = self.entries["Telefone"].get()

        try:
            if self.modo == "novo":
                # Insere novo cliente
                query = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
                params = (nome, email, telefone)
                db.executar_comando(query, params)
                messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")

            elif self.modo == "editar":
                # Atualiza cliente existente
                query = "UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?"
                params = (nome, email, telefone, self.cliente_id)
                db.executar_comando(query, params)
                messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")

            # Se chegou aqui, salvou com sucesso
            self.callback_sucesso()  # Chama a função para recarregar a lista na tela principal
            self.destroy()  # Fecha a janela do formulário

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")