# Arquivo de backup gerado em: 2025-08-28 11:04:10
import sqlite3
from datetime import datetime

def setup_database():
    print("Iniciando a criação e população do banco de dados a partir do backup...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Cria as tabelas (código de criação que já conhecemos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, category TEXT NOT NULL,
            description TEXT NOT NULL, price TEXT NOT NULL, link TEXT NOT NULL,
            votes INTEGER NOT NULL DEFAULT 0, base_popularity INTEGER NOT NULL DEFAULT 50,
            logo_url TEXT, date_added TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL
        )
    ''')

    # A lista de ferramentas gerada a partir do banco de dados atual
    initial_tools_with_score = [
        ('ChatGPT', 'ajuda-pesquisas', 'Modelo de linguagem versátil para responder perguntas, escrever textos e muito mais.', 'Plano gratuito disponível. ChatGPT Plus por US$ 20/mês.', 'https://chat.openai.com', 100),
        ('Google Gemini', 'ajuda-pesquisas', 'IA do Google que auxilia na pesquisa, geração de conteúdo e integração com o ecossistema do Google.', 'Versão gratuita disponível. Gemini Advanced a partir de US$ 19,99/mês.', 'https://gemini.google.com', 99),
        ('GitHub Copilot', 'programacao', 'Assistente de programação que sugere trechos de código em tempo real.', 'Planos a partir de US$ 10/mês.', 'https://github.com/features/copilot', 98),
        ('Midjourney', 'arte', 'IA de geração de imagens artísticas disponível via Discord.', 'Planos a partir de US$ 10/mês.', 'https://midjourney.com', 97),
        ('DALL-E 3', 'arte', 'IA da OpenAI para gerar imagens realistas a partir de prompts.', 'Incluído no ChatGPT Plus.', 'https://openai.com/dall-e-3', 96),
        ('Stable Diffusion', 'arte', 'Modelo de geração de imagens open source baseado em difusão.', 'Gratuito. Serviços pagos de terceiros.', 'https://stability.ai', 95),
        ('Microsoft Copilot', 'enterprise', 'Assistente de IA integrado ao Microsoft 365 (Word, Excel, Outlook).', 'Incluído em planos do Microsoft 365. A partir de US$ 30/mês por usuário.', 'https://www.microsoft.com/microsoft-365/copilot', 94),
        ('Canva AI', 'design', 'Conjunto de ferramentas de IA para design, geração de texto e imagens.', 'Gratuito com versão Pro a partir de US$ 14,99/mês.', 'https://canva.com', 93),
        ('Claude', 'ajuda-pesquisas', 'IA da Anthropic com foco em segurança, contexto longo e ajuda em escrita complexa.', 'Plano gratuito disponível. Claude Pro a partir de US$ 20/mês.', 'https://claude.ai', 92),
        ('Perplexity AI', 'ajuda-pesquisas', 'Ferramenta de pesquisa que fornece respostas diretas com citações, ideal para pesquisas acadêmicas.', 'Plano gratuito disponível. Versão Pro por US$ 20/mês.', 'https://www.perplexity.ai', 91),
        ('Adobe Firefly', 'gera-imagens', 'IA de geração de imagens da Adobe integrada ao Photoshop e Illustrator.', 'Incluído no Adobe Creative Cloud. Planos a partir de US$ 20/mês.', 'https://www.adobe.com/sensei/generative-ai/firefly.html', 90),
        ('Grammarly', 'escrita', 'Assistente de escrita que sugere melhorias em gramática, estilo e tom.', 'Plano gratuito disponível. Premium a partir de US$ 12/mês.', 'https://grammarly.com', 89),
        ('Notion AI', 'produtividade', 'Assistente de escrita e resumo integrado ao Notion para organização de tarefas e textos.', 'Plano gratuito disponível. Notion Plus a partir de US$ 8/mês.', 'https://www.notion.so', 88),
        ('Runway', 'gera-videos-complexos', 'Suite completa de edição de vídeo com IA, incluindo geração de vídeo a partir de texto (Gen-2).', 'Plano gratuito com limitações. Planos pagos a partir de US$ 12/mês.', 'https://runwayml.com', 87),
        ('ElevenLabs', 'gera-voz', 'Ferramenta avançada para geração de voz realista e clonagem de voz.', 'Plano gratuito com créditos. Planos pagos a partir de US$ 5/mês.', 'https://elevenlabs.io', 86),
        ('Suno AI', 'gera-musica', 'Crie músicas completas (vocais e instrumentos) a partir de uma simples descrição de texto.', 'Plano gratuito com créditos. Planos pagos a partir de US$ 8/mês.', 'https://www.suno.ai', 85),
        ('Zapier AI', 'automacao', 'Ferramenta de automação que conecta aplicativos e cria fluxos inteligentes.', 'Plano gratuito disponível. Planos pagos a partir de US$ 19,99/mês.', 'https://zapier.com', 84),
        ('Hugging Face', 'plataforma-modelos', 'Hub colaborativo de modelos open-source de IA.', 'Gratuito. Serviços enterprise pagos.', 'https://huggingface.co', 83),
        ('DeepL', 'traducao', 'Ferramenta de tradução de alta qualidade baseada em IA.', 'Plano gratuito disponível. Pro a partir de US$ 8/mês.', 'https://deepl.com', 82),
        ('Jasper', 'ajuda-pesquisas', 'Assistente de escrita com IA que ajuda a criar conteúdo otimizado para blogs, marketing e redes sociais.', 'Planos a partir de US$ 49/mês.', 'https://www.jasper.ai', 81),
        ('Otter.ai', 'transcricao', 'Assistente de reuniões que gera transcrições automáticas e resumos.', 'Plano gratuito disponível. Planos pagos a partir de US$ 10/mês.', 'https://otter.ai', 80),
        ('Synthesia', 'gera-videos', 'Cria vídeos com avatares de IA realistas a partir de texto, ideal para treinamentos e comunicação corporativa.', 'Planos a partir de US$ 29/mês.', 'https://www.synthesia.io', 79),
        ('HeyGen', 'gera-videos', 'Crie vídeos com avatares e traduza a fala para diferentes idiomas mantendo a voz original.', 'Plano gratuito com créditos. Planos pagos a partir de US$ 24/mês.', 'https://www.heygen.com', 78),
        ('Pika Labs', 'gera-videos-complexos', 'Ferramenta poderosa para gerar e editar vídeos a partir de texto e imagens.', 'Plano gratuito com créditos. Planos pagos a partir de US$ 8/mês.', 'https://pika.art', 77),
        ('Descript', 'edicao-audio-video', 'Editor de áudio e vídeo baseado em IA que permite editar pela transcrição de texto.', 'Plano gratuito disponível. Planos pagos a partir de US$ 12/mês.', 'https://www.descript.com', 76),
        ('Udio', 'gera-musica', 'Ferramenta de geração de música a partir de texto, com alta qualidade sonora.', 'Versão beta gratuita.', 'https://www.udio.com', 75),
        ('Quillbot', 'escrita', 'Ferramenta de parafrasear textos, checar gramática e gerar resumos.', 'Plano gratuito disponível. Premium a partir de US$ 9,95/mês.', 'https://quillbot.com', 74),
        ('Writesonic', 'ajuda-pesquisas', 'IA para geração de textos longos e curtos, com foco em SEO e marketing.', 'Plano gratuito com limitações. Planos pagos a partir de US$ 16/mês.', 'https://writesonic.com', 73),
        ('Fireflies.ai', 'transcricao', 'IA para gravação e resumo de reuniões em plataformas como Zoom e Meet.', 'Plano gratuito disponível. Planos pagos a partir de US$ 10/mês.', 'https://fireflies.ai', 72),
        ('Copy.ai', 'ajuda-pesquisas', 'Ferramenta de marketing e escrita automatizada para criação de textos persuasivos.', 'Plano gratuito disponível. Planos pagos a partir de US$ 36/mês.', 'https://www.copy.ai', 71),
        ('IBM WatsonX', 'enterprise', 'Plataforma de IA da IBM para empresas com modelos de linguagem e analytics.', 'price sob consulta.', 'https://www.ibm.com/watsonx', 70),
        ('Amazon Bedrock', 'enterprise', 'Serviço da AWS para construir aplicações com modelos de IA generativa.', 'price sob consulta.', 'https://aws.amazon.com/bedrock', 69),
        ('Vertex AI', 'enterprise', 'Plataforma de machine learning da Google Cloud para implantar modelos.', 'price sob consulta.', 'https://cloud.google.com/vertex-ai', 68),
        ('Khanmigo', 'educacao', 'Tutor virtual de IA da Khan Academy que auxilia alunos em diversas matérias.', 'Gratuito. Premium sob consulta.', 'https://khanacademy.org/khan-labs', 67),
        ('Leonardo AI', 'arte', 'Plataforma de criação de imagens para jogos, ilustrações e concept art.', 'Planos gratuitos e pagos.', 'https://leonardo.ai', 66),
        ('Gamma', 'gera-imagens', 'Cria apresentações, documentos e páginas web visualmente impressionantes a partir de texto.', 'Plano gratuito com créditos. Planos Pro a partir de US$ 16/mês.', 'https://gamma.app', 65),
        ('Lumen5', 'gera-videos', 'Plataforma que transforma posts de blog e textos em vídeos curtos para mídias sociais rapidamente.', 'Plano gratuito disponível. Planos pagos a partir de US$ 19/mês.', 'https://lumen5.com', 64),
    ]
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tools_to_insert = [
        (name, cat, desc, price, link, pop, '', now_str) for name, cat, desc, price, link, pop in initial_tools_with_score
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO tools (name, category, description, price, link, base_popularity, logo_url, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        tools_to_insert
    )
    
    print(f" -> {cursor.rowcount} novas IAs do backup foram inseridas.")
    
    conn.commit()
    conn.close()
    print("\n✅ Processo de setup a partir do backup concluído!")

if __name__ == '__main__':
    setup_database()
