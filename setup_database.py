import sqlite3

def migrate_database():
    """
    Verifica o banco de dados e aplica as atualizações necessárias
    de forma segura, sem apagar dados existentes.
    """
    print("Iniciando verificação e migração do banco de dados...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # --- Etapa 1: Garantir que a tabela 'users' existe ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # --- Etapa 2: Verificar e Adicionar a Coluna 'email' ---
    print("Verificando tabela 'users' para a coluna 'email'...")
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'email' not in columns:
        # Adiciona a coluna, permitindo valores nulos temporariamente
        cursor.execute('ALTER TABLE users ADD COLUMN email TEXT')
        # Define um valor placeholder único para registros antigos
        cursor.execute("UPDATE users SET email = 'user_' || id || '@placeholder.email' WHERE email IS NULL")
        # AGORA, podemos adicionar a restrição NOT NULL UNIQUE se quisermos,
        # mas vamos manter simples por enquanto.
        print(" -> Coluna 'email' adicionada e registros antigos atualizados com um placeholder.")
    else:
        print(" -> Coluna 'email' já existe.")

    # ... (o resto do seu script de setup, como a criação da tabela 'tools' e 'favorites', pode continuar aqui)

    conn.commit()
    conn.close()
    
    print("\n✅ Migração do banco de dados concluída com sucesso!")

if __name__ == '__main__':
    migrate_database()