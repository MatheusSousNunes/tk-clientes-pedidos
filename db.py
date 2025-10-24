import sqlite3
import logging

# Define o nome do arquivo do banco de dados
DB_NAME = 'app_data.db'


def inicializar_banco():
    """
    Cria as tabelas no banco de dados se elas não existirem.
    Baseado no Prompt 1: clientes, pedidos, itens_pedido.
    """
    # Usamos 'with' para garantir que a conexão seja fechada
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # --- Tabela de Clientes ---
        #  (id, nome, email, telefone)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT,
                telefone TEXT
            )
        ''')

        # --- Tabela de Pedidos ---
        #  (id, cliente_id, data, total)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                data TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')

        # --- Tabela de Itens do Pedido ---
        #  (id, pedido_id, produto, quantidade, preco_unit)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unit REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            )
        ''')

        conn.commit()
        logging.info("Banco de dados inicializado com sucesso.")


def executar_comando(query, params=()):
    """
    Função genérica para executar comandos (INSERT, UPDATE, DELETE).
    Usa parâmetros para evitar SQL Injection.
     "executar comandos parametrizados com tratamento de erros."
    Retorna o ID do último item inserido (útil para pedidos).
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        # [cite: 42] "try/except com logs simples."
        logging.error(f"Erro ao executar comando: {e}\nQuery: {query}\nParams: {params}")
        return None  # Indica que houve um erro


def executar_select(query, params=()):
    """
    Função genérica para executar consultas (SELECT).
    Usa parâmetros para evitar SQL Injection.
     "executar comandos parametrizados com tratamento de erros."
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Row_factory torna o resultado um dicionário (ex: {'nome': 'Ana'})
            # em vez de uma tupla (ex: ('Ana',)). Fica mais fácil de usar.
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            # Converte os resultados para dicionários Python puros
            return [dict(row) for row in resultados]
    except sqlite3.Error as e:
        logging.error(f"Erro ao executar select: {e}\nQuery: {query}\nParams: {params}")
        return []  # Retorna lista vazia em caso de erro


# --- Configuração de Log (para try/except) ---
# [cite: 42] "logs simples"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ... (todo o código existente de db.py) ...
# ... (depois da função executar_select) ...

def salvar_pedido_e_itens(cliente_id, data, total, itens):
    """
    Salva um novo pedido e seus itens de forma transacional.
    Baseado no Prompt 4. [cite: 39, 40]
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # 1. Inserir o Pedido principal
        query_pedido = "INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)"
        cursor.execute(query_pedido, (cliente_id, data, total))

        # 2. Obter o ID do pedido que acabamos de criar
        pedido_id = cursor.lastrowid

        # 3. Inserir os Itens do Pedido
        query_item = "INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unit) VALUES (?, ?, ?, ?)"

        # Prepara uma lista de tuplas para inserir os itens
        itens_para_salvar = []
        for item in itens:
            itens_para_salvar.append(
                (pedido_id, item['produto'], item['quantidade'], item['preco_unit'])
            )

        # executemany é mais eficiente para inserir vários itens
        cursor.executemany(query_item, itens_para_salvar)

        # 5. Se tudo deu certo, commita a transação
        conn.commit()
        logging.info(f"Pedido {pedido_id} salvo com sucesso.")
        return pedido_id

    except sqlite3.Error as e:
        # "try/except com logs simples." [cite: 42]
        logging.error(f"Erro ao salvar pedido transacional: {e}")
        if conn:
            conn.rollback()  # Desfaz todas as mudanças se houver erro
        return None
    finally:
        if conn:
            conn.close()


# ... (o resto do arquivo, como logging.basicConfig e if __name__ ==...) ...

# --- Código de inicialização ---
# Este 'if' faz com que a função só rode
# quando o arquivo db.py é executado, mas não quando é importado.
# (Boa prática, mas para este projeto, podemos simplificar e chamar no main.py)
if __name__ == '__main__':
    print("Inicializando o banco de dados...")
    inicializar_banco()
    print("Banco de dados pronto.")