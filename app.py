import os
import sqlite3
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import feedparser
from time import time
import requests
from serpapi import GoogleSearch
from PIL import Image
import io
import ssl
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
load_dotenv()
app = Flask(__name__)
# CONFIGURAÇÃO DE COOKIES PARA PRODUÇÃO
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", os.urandom(24))
cors = CORS(app, resources={
    r"/api/*": {
        "origins": ["https://ainavigator-tools.netlify.app", "http://127.0.0.1:8000"],
        "supports_credentials": True
    }
})
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

# --- CONFIGURAÇÃO DE CORS PARA PRODUÇÃO E DESENVOLVIMENTO ---
FRONTEND_URL = "https://ainavigator-tools.netlify.app"


# --- MODELO E CARREGADOR DE USUÁRIO ---
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return User(id=user_data['id'], username=user_data['username']) if user_data else None

# --- FUNÇÕES AUXILIARES GLOBAIS ---
def get_db_connection():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def sanitize_filename(name):
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s_-]+', '_', name)
    return name.strip('_')

def find_image_in_entry(entry):
    image_url = None
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail: image_url = entry.media_thumbnail[0].get('url')
    elif hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media and media.get('medium') == 'image': image_url = media.get('url'); break
    if not image_url and hasattr(entry, 'summary'):
        matches = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if matches: image_url = matches.group(1)
    return image_url

def find_and_download_logo(tool_name):
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if not serpapi_key: return None
    print(f"🤖 Auto-buscando logo para: {tool_name}...")
    params = {"engine": "google_images", "q": f"{tool_name} logo png transparent", "api_key": serpapi_key, "tbs": "ic:trans"}
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if "images_results" in results and len(results["images_results"]) > 0:
            image_url = results["images_results"][0]["original"]
            response = requests.get(image_url, stream=True, timeout=10)
            if response.status_code == 200:
                filename = sanitize_filename(tool_name) + ".png"
                if not os.path.exists('logos'): os.makedirs('logos')
                filepath = os.path.join('logos', filename)
                with open(filepath, 'wb') as f: f.write(response.content)
                return filepath.replace('\\', '/')
    except Exception as e:
        print(f"❌ Erro na busca de logo para '{tool_name}': {e}")
    return None

# --- ROTAS DA API PÚBLICA ---
@app.route('/api/tools', methods=['GET'])
def get_tools():
    conn = get_db_connection()
    tools = conn.execute('SELECT * FROM tools ORDER BY votes DESC, base_popularity DESC, name ASC').fetchall()
    conn.close()
    return jsonify([dict(tool) for tool in tools])

@app.route('/api/tools/newest', methods=['GET'])
def get_newest_tools():
    conn = get_db_connection()
    tools = conn.execute('SELECT * FROM tools ORDER BY date_added DESC LIMIT 12').fetchall()
    conn.close()
    return jsonify([dict(tool) for tool in tools])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    query = "SELECT category, COUNT(id) as tool_count FROM tools GROUP BY category ORDER BY category ASC"
    categories_data = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(row) for row in categories_data])
    
@app.route('/api/vote/<int:tool_id>', methods=['POST'])
def vote(tool_id):
    conn = get_db_connection()
    conn.execute('UPDATE tools SET votes = votes + 1 WHERE id = ?', (tool_id,))
    conn.commit()
    new_vote_count = conn.execute('SELECT votes FROM tools WHERE id = ?', (tool_id,)).fetchone()
    conn.close()
    return jsonify({'votes': new_vote_count['votes']}) if new_vote_count else ({'error': 'Tool not found'}, 404)

@app.route('/api/unvote/<int:tool_id>', methods=['POST'])
def unvote(tool_id):
    conn = get_db_connection()
    conn.execute('UPDATE tools SET votes = votes - 1 WHERE id = ? AND votes > 0', (tool_id,))
    conn.commit()
    new_vote_count = conn.execute('SELECT votes FROM tools WHERE id = ?', (tool_id,)).fetchone()
    conn.close()
    return jsonify({'votes': new_vote_count['votes']}) if new_vote_count else ({'error': 'Tool not found'}, 404)

@app.route('/api/glossary', methods=['GET'])
def get_glossary_terms():
    try:
        with open('glossary.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data.sort(key=lambda x: x['term'])
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo glossary.json não encontrado."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROTA DE NOTÍCIAS ---
NEWS_FEEDS = {
    'Google News (IA)': 'https://news.google.com/rss/search?q=Intelig%C3%AAncia+Artificial&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    'Ben\'s Bites': 'https://bensbites.beehiiv.com/rss',
}
news_cache = {'articles': [], 'last_updated': 0}
@app.route('/api/news', methods=['GET'])
def get_news():
    if (time() - news_cache['last_updated']) < 1800 and news_cache['articles']:
        return jsonify(news_cache['articles'])
    print("🔥 Forçando busca de notícias frescas...")
    all_articles = []
    user_agent_header = {'User-Agent': 'Mozilla/5.0'}
    for source, url in NEWS_FEEDS.items():
        try:
            response = requests.get(url, headers=user_agent_header, timeout=10)
            feed = feedparser.parse(response.content)
            if not feed.entries: continue
            for entry in feed.entries[:5]:
                image_url = find_image_in_entry(entry)
                all_articles.append({'source': source, 'title': entry.title, 'link': entry.link, 'published': entry.get('published', ''), 'image_url': image_url or 'logos/news_placeholder.png'})
        except Exception as e:
            print(f"Erro ao buscar notícias de {source}: {e}")
    if all_articles:
        news_cache['articles'] = all_articles
        news_cache['last_updated'] = time()
    return jsonify(news_cache['articles'])

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email') # <-- Pega o novo campo
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({'success': False, 'message': 'Username, email, and password are required.'}), 400
        
    conn = get_db_connection()
    user_exists = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
    if user_exists:
        conn.close()
        return jsonify({'success': False, 'message': 'Username or email already exists.'}), 409
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    # Adiciona o email ao INSERT
    conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, hashed_password))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Registration successful! Please login.'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user_data and bcrypt.check_password_hash(user_data['password_hash'], password):
        user = User(id=user_data['id'], username=user_data['username'])
        login_user(user, remember=True)
        return jsonify({'success': True, 'message': 'Login successful!', 'username': user.username})
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@app.route('/api/status')
def status():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.username})
    else:
        return jsonify({'logged_in': False})

# --- ROTAS DE FAVORITOS ---
@app.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    conn = get_db_connection()
    fav_rows = conn.execute('SELECT tool_id FROM favorites WHERE user_id = ?', (current_user.id,)).fetchall()
    conn.close()
    return jsonify({'favorites': [row['tool_id'] for row in fav_rows]})

@app.route('/api/favorites/tools', methods=['GET'])
@login_required
def get_favorite_tools():
    conn = get_db_connection()
    query = "SELECT t.* FROM tools t JOIN favorites f ON t.id = f.tool_id WHERE f.user_id = ?"
    tools = conn.execute(query, (current_user.id,)).fetchall()
    conn.close()
    return jsonify([dict(tool) for tool in tools])

@app.route('/api/favorites/toggle/<int:tool_id>', methods=['POST'])
@login_required
def toggle_favorite(tool_id):
    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM favorites WHERE user_id = ? AND tool_id = ?', (current_user.id, tool_id)).fetchone()
    if existing:
        conn.execute('DELETE FROM favorites WHERE user_id = ? AND tool_id = ?', (current_user.id, tool_id))
        action = 'removed'
    else:
        conn.execute('INSERT INTO favorites (user_id, tool_id) VALUES (?, ?)', (current_user.id, tool_id))
        action = 'added'
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'action': action})

# --- ROTAS DO PAINEL DE ADMIN ---
@app.route('/api/admin/tools/add', methods=['POST'])
def add_tool():
    data = request.json
    logo_path = data.get('logo_url', '')
    if not logo_path:
        logo_path = find_and_download_logo(data['name'])
    date_added_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO tools (name, category, description, price, link, base_popularity, logo_url, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (data['name'], data['category'], data['description'], data['price'], data['link'], data.get('base_popularity', 50), logo_path or '', date_added_str)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({'error': 'Uma ferramenta com este nome já existe.'}), 409
    conn.close()
    return jsonify({'success': True, 'logo_found': bool(logo_path)}), 201

@app.route('/api/admin/tools/batch-add', methods=['POST'])
def batch_add_tools():
    data = request.json['data'].strip()
    lines = data.split('\n')
    conn = get_db_connection()
    tools_added = 0
    logos_found = 0
    date_added_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for line in lines:
        try:
            parts = [p.strip() for p in line.split(';')]
            if len(parts) >= 6:
                name, category, description, price, link, popularity = parts[:6]
                logo_url = parts[6] if len(parts) > 6 else ''
                if not logo_url:
                    logo_url = find_and_download_logo(name)
                conn.execute(
                    'INSERT OR IGNORE INTO tools (name, category, description, price, link, base_popularity, logo_url, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (name, category, description, price, link, int(popularity), logo_url or '', date_added_str)
                )
                tools_added += 1
                if logo_url: logos_found += 1
        except Exception as e:
            print(f"Erro ao processar linha: '{line}'. Erro: {e}")
            continue
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'tools_added': tools_added, 'logos_found': logos_found})

@app.route('/api/admin/tools/delete/<int:tool_id>', methods=['DELETE'])
def delete_tool(tool_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tools WHERE id = ?', (tool_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))