import sqlite3
from datetime import datetime

def setup_database():
    print("Iniciando a criação e população do banco de dados...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Tabela de Ferramentas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, category TEXT NOT NULL,
            description TEXT NOT NULL, price TEXT NOT NULL, link TEXT NOT NULL,
            votes INTEGER NOT NULL DEFAULT 0, base_popularity INTEGER NOT NULL DEFAULT 50,
            logo_url TEXT, date_added TEXT
        )
    ''')
    print(" -> Tabela 'tools' verificada/criada.")

    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL
        )
    ''')
    print(" -> Tabela 'users' verificada/criada.")
    
    # Tabela de Favoritos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER NOT NULL,
            tool_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, tool_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (tool_id) REFERENCES tools (id) ON DELETE CASCADE
        )
    ''')
    print(" -> Tabela 'favorites' verificada/criada.")

    conn.commit()
    conn.close()
    print("\n✅ Processo de setup do banco de dados concluído!")

if __name__ == '__main__':
    setup_database()