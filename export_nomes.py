import sqlite3

def export_tool_names():
    """
    Lê o banco de dados e exporta o nome de cada ferramenta
    para um arquivo de texto chamado 'lista_ias.txt'.
    """
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Seleciona apenas o nome de todas as ferramentas
        cursor.execute('SELECT name FROM tools ORDER BY name ASC')
        tools = cursor.fetchall()
        
        conn.close()
        
        # Abre o arquivo de texto para escrita
        with open('lista_ias.txt', 'w', encoding='utf-8') as f:
            for tool in tools:
                f.write(tool['name'] + '\n')
                
        print(f"Sucesso! {len(tools)} nomes de IAs foram exportados para o arquivo 'lista_ias.txt'.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == '__main__':
    export_tool_names()