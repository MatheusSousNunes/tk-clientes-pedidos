Atividade: Cadastro de Clientes & Pedidos com Tkinter
Este projeto é uma aplicação de desktop simples para gerenciar clientes e pedidos, utilizando Tkinter para a interface gráfica e SQLite para a persistência de dados.


O sistema permite:

Cadastrar, listar, editar, buscar e excluir clientes.

Criar novos pedidos associados a clientes.

Adicionar múltiplos itens a um pedido com cálculo automático de total.

Como Rodar
Pré-requisitos
Python 3.10 ou superior.

Nenhuma biblioteca externa é necessária (utiliza apenas a biblioteca padrão do Python, como Tkinter e SQLite).

Passos para Execução
Clone ou baixe este repositório.

(Opcional, mas recomendado) Crie e ative um ambiente virtual:

Bash

python -m venv .venv
# No Windows (CMD):
.venv\Scripts\activate
Execute o arquivo principal para iniciar o banco de dados e abrir o programa:

Bash

python main.py
Ao executar o main.py pela primeira vez, o arquivo de banco de dados app_data.db será criado automaticamente.

Registro de IA (Prompts Principais)
Este projeto foi desenvolvido com o auxílio de um assistente de IA para prototipar e gerar trechos de código, conforme as regras da atividade. Abaixo estão os principais prompts utilizados e as decisões tomadas:


1. Prompt 1: Modelagem e DB 


Prompt Utilizado (conforme PDF): "Crie, para um app Tkinter, o esquema de SQLite com tabelas clientes (id, nome, email, telefone) e pedidos (id, cliente_id, data, total) e itens_pedido (id, pedido_id, produto, quantidade, preco_unit). Gere funções Python em db.py para inicializar o banco e executar comandos parametrizados com tratamento de erros." 

O que foi aceito/ajustado: O prompt foi aceito integralmente. O assistente gerou o db.py com:

inicializar_banco(): Cria as 3 tabelas.

executar_comando(): Função genérica para INSERT, UPDATE, DELETE.

executar_select(): Função genérica para SELECT que retorna dicionários.

Posteriormente, foi adicionada a função salvar_pedido_e_itens para atender ao Prompt 4.

2. Prompts 2 e 3: Formulário e Lista de Clientes 



Prompts Utilizados (combinados): "Gere um formulário Tkinter (janela Toplevel) para cadastrar/editar Clientes..." e "Crie um frame Tkinter com Treeview para listar clientes, com barra de busca por nome/email e botões Novo/Editar/Excluir..." 


O que foi aceito/ajustado: Os prompts foram usados para criar o arquivo views/clientes_view.py.

Aceito: A estrutura de duas classes foi aceita: ClientesView (para a lista/busca) e FormularioCliente (para a janela Toplevel).


Aceito: O uso de ttk.Treeview para a lista e messagebox.askyesno para a confirmação de exclusão.


Aceito: A lógica de validação de campos (nome obrigatório, email, telefone) foi implementada com re e messagebox.

3. Prompt 4: Pedido com Itens 


Prompt Utilizado (conforme PDF): "Implemente uma janela Tkinter para criar Pedido: selecione Cliente (Combobox), campo Data (hoje por padrão), tabela de itens (produto/quantidade/preço), botões Adicionar/Remover item e cálculo automático do total. Salve em pedidos e itens_pedido de forma transacional." 

O que foi aceito/ajustado: Este foi o prompt mais complexo.

Aceito: A estrutura do formulário (FormularioPedido) foi gerada conforme solicitado (ComboBox, Treeview para itens, etc.).


Aceito: A função atualizar_total() foi criada para o cálculo automático.

Ajuste: Para a "forma transacional", foi criada a função salvar_pedido_e_itens no db.py, que utiliza conn.commit() e conn.rollback() para garantir que o pedido e seus itens sejam salvos juntos, ou nenhum deles.

4. Prompt 5: UX e Validações 


Prompt Utilizado (conforme PDF): "Melhore UX do app: mensagens amigáveis (messagebox), validações com feedback, prevenção de fechar janela com dados não salvos, e try/except com logs simples." 

O que foi aceito/ajustado:

messagebox e try/except já haviam sido implementados nos prompts anteriores.

Ajuste: A "prevenção de fechar janela" foi implementada manualmente nos formulários FormularioCliente e FormularioPedido usando o método self.protocol("WM_DELETE_WINDOW", self.on_closing), que chama uma função de confirmação.
