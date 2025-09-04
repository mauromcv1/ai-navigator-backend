import os
import sqlite3
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from time import time
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, text
import feedparser
import requests
from serpapi import GoogleSearch
from PIL import Image
import io
import ssl

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", os.urandom(24))

# --- CONFIGURAÇÃO DE AMBIENTE E BANCO DE DADOS "CAMALEÃO" ---
IS_PRODUCTION = os.getenv('RENDER', False)
DATABASE_URL = os.getenv('DATABASE_URL')
if IS_PRODUCTION:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    origins = ["https://getainavigator.app", "https://www.getainavigator.app"]
else:
    DATABASE_URL = 'sqlite:///database.db'
    origins = ["http://127.0.0.1:8000"]

CORS(app, origins=origins, supports_credentials=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# --- MODELO E CARREGADOR DE USUÁRIO ---
class User(UserMixin):
    def __init__(self, id, username): self.id = id; self.username = username

@login_manager.user_loader
def load_user(user_id):
    if not engine: return None
    with engine.connect() as conn:
        user_data = conn.execute(text("SELECT * FROM users WHERE id = :id"), {'id': int(user_id)}).fetchone()
    return User(id=user_data.id, username=user_data.username) if user_data else None

# --- FUNÇÕES AUXILIARES GLOBAIS ---
def sanitize_filename(name):
    name = name.lower(); name = re.sub(r'[^\w\s-]', '', name); name = re.sub(r'[\s_-]+', '_', name); return name.strip('_')

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
                logos_dir = 'logos'
                if not os.path.exists(logos_dir): os.makedirs(logos_dir)
                filepath = os.path.join(logos_dir, filename)
                with open(filepath, 'wb') as f: f.write(response.content)
                return os.path.join('logos', filename).replace('\\', '/')
    except Exception as e:
        print(f"❌ Erro na busca de logo para '{tool_name}': {e}")
    return None

# --- ROTAS DA API PÚBLICA ---
@app.route('/api/tools', methods=['GET'])
def get_tools():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM tools ORDER BY votes DESC, base_popularity DESC, name ASC'))
        tools = result.fetchall()
    return jsonify([row._asdict() for row in tools])

@app.route('/api/tools/newest', methods=['GET'])
def get_newest_tools():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM tools ORDER BY date_added DESC LIMIT 12'))
        tools = result.fetchall()
    return jsonify([row._asdict() for row in tools])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        query = text("SELECT category, COUNT(id) as tool_count FROM tools GROUP BY category ORDER BY category ASC")
        result = conn.execute(query)
        categories_data = result.fetchall()
    return jsonify([row._asdict() for row in categories_data])

@app.route('/api/vote/<int:tool_id>', methods=['POST'])
def vote(tool_id):
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        conn.execute(text('UPDATE tools SET votes = votes + 1 WHERE id = :id'), {'id': tool_id}); conn.commit()
        result = conn.execute(text('SELECT votes FROM tools WHERE id = :id'), {'id': tool_id}).fetchone()
    return jsonify({'votes': result.votes}) if result else ({'error': 'Tool not found'}, 404)

@app.route('/api/unvote/<int:tool_id>', methods=['POST'])
def unvote(tool_id):
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        conn.execute(text('UPDATE tools SET votes = votes - 1 WHERE id = :id AND votes > 0'), {'id': tool_id}); conn.commit()
        result = conn.execute(text('SELECT votes FROM tools WHERE id = :id'), {'id': tool_id}).fetchone()
    return jsonify({'votes': result.votes}) if result else ({'error': 'Tool not found'}, 404)

@app.route('/api/glossary', methods=['GET'])
def get_glossary_terms():
    try:
        with open('glossary.json', 'r', encoding='utf-8') as f:
            data = json.load(f); data.sort(key=lambda x: x['term']); return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROTA DE NOTÍCIAS ---
NEWS_FEEDS = { 'Google News (IA)': '...', 'Ben\'s Bites': '...' }
news_cache = {'articles': [], 'last_updated': 0}
@app.route('/api/news', methods=['GET'])
def get_news():
    if (time() - news_cache['last_updated']) < 1800 and news_cache['articles']:
        return jsonify(news_cache['articles'])
    all_articles = []
    # ... (código da função get_news)
    return jsonify(news_cache['articles'])
    pass



# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/api/register', methods=['POST'])
def register():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    data = request.json
    username, email, password = data.get('username'), data.get('email'), data.get('password')
    if not all([username, email, password]): return jsonify({'success': False, 'message': 'Missing fields'}), 400
    with engine.connect() as conn:
        query = text("SELECT id FROM users WHERE username = :username OR email = :email")
        if conn.execute(query, {'username': username, 'email': email}).fetchone():
            return jsonify({'success': False, 'message': 'Username or email already exists.'}), 409
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        insert_query = text("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)")
        conn.execute(insert_query, {'username': username, 'email': email, 'password_hash': hashed_password}); conn.commit()
    return jsonify({'success': True, 'message': 'Registration successful!'})

@app.route('/api/login', methods=['POST'])
def login():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    data = request.json
    username, password = data.get('username'), data.get('password')
    with engine.connect() as conn:
        user_data = conn.execute(text("SELECT * FROM users WHERE username = :username"), {'username': username}).fetchone()
    if user_data and bcrypt.check_password_hash(user_data.password_hash, password):
        user = User(id=user_data.id, username=user_data.username); login_user(user, remember=True)
        return jsonify({'success': True, 'username': user.username})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user(); return jsonify({'success': True})

@app.route('/api/status')
def status():
    if not engine: return jsonify({'logged_in': False})
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.username})
    return jsonify({'logged_in': False})

# --- ROTAS DE FAVORITOS ---
@app.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        fav_rows = conn.execute(text('SELECT tool_id FROM favorites WHERE user_id = :uid'), {'uid': current_user.id}).fetchall()
    return jsonify({'favorites': [row.tool_id for row in fav_rows]})

@app.route('/api/favorites/tools', methods=['GET'])
@login_required
def get_favorite_tools():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        query = text("SELECT t.* FROM tools t JOIN favorites f ON t.id = f.tool_id WHERE f.user_id = :uid")
        tools = conn.execute(query, {'uid': current_user.id}).fetchall()
    return jsonify([row._asdict() for row in tools])

@app.route('/api/favorites/toggle/<int:tool_id>', methods=['POST'])
@login_required
def toggle_favorite(tool_id):
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        query = text("SELECT * FROM favorites WHERE user_id = :uid AND tool_id = :tid")
        existing = conn.execute(query, {'uid': current_user.id, 'tid': tool_id}).fetchone()
        if existing:
            conn.execute(text('DELETE FROM favorites WHERE user_id = :uid AND tool_id = :tid'), {'uid': current_user.id, 'tid': tool_id})
            action = 'removed'
        else:
            conn.execute(text('INSERT INTO favorites (user_id, tool_id) VALUES (:uid, :tid)'), {'uid': current_user.id, 'tid': tool_id})
            action = 'added'
        conn.commit()
    return jsonify({'success': True, 'action': action})

# --- ROTAS DO PAINEL DE ADMIN ---
@app.route('/api/admin/tools/add', methods=['POST'])
def add_tool():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    data = request.json; logo_path = data.get('logo_url', '')
    if not logo_path: logo_path = find_and_download_logo(data['name'])
    date_added_str = datetime.now()
    with engine.connect() as conn:
        try:
            insert_query = text('INSERT INTO tools (name, category, description, price, link, base_popularity, logo_url, date_added) VALUES (:name, :category, :description, :price, :link, :base_popularity, :logo_url, :date_added)')
            conn.execute(insert_query, {'name': data['name'], 'category': data['category'], 'description': data['description'], 'price': data['price'], 'link': data['link'], 'base_popularity': data.get('base_popularity', 50), 'logo_url': logo_path or '', 'date_added': date_added_str}); conn.commit()
        except Exception as e:
            return jsonify({'error': f'A ferramenta com este nome provavelmente já existe. Erro: {e}'}), 409
    return jsonify({'success': True, 'logo_found': bool(logo_path)}), 201

@app.route('/api/admin/tools/batch-add', methods=['POST'])
def batch_add_tools():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    data = request.json['data'].strip(); lines = data.split('\n'); tools_added = 0; logos_found = 0; date_added_str = datetime.now()
    with engine.connect() as conn:
        for line in lines:
            try:
                parts = [p.strip() for p in line.split(';')]
                if len(parts) >= 6:
                    name, category, description, price, link, popularity = parts[:6]; logo_url = parts[6] if len(parts) > 6 else ''
                    if not logo_url: logo_url = find_and_download_logo(name)
                    insert_query = text('INSERT INTO tools (name, category, description, price, link, base_popularity, logo_url, date_added) VALUES (:name, :category, :description, :price, :link, :base_popularity, :logo_url, :date_added) ON CONFLICT (name) DO NOTHING')
                    conn.execute(insert_query, {'name': name, 'category': category, 'description': description, 'price': price, 'link': link, 'base_popularity': int(popularity), 'logo_url': logo_url or '', 'date_added': date_added_str})
                    tools_added += 1;
                    if logo_url: logos_found += 1
            except Exception as e:
                print(f"Erro ao processar linha em lote: '{line}'. Erro: {e}")
        conn.commit()
    return jsonify({'success': True, 'tools_added': tools_added, 'logos_found': logos_found})

@app.route('/api/admin/tools/delete/<int:tool_id>', methods=['DELETE'])
def delete_tool(tool_id):
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM tools WHERE id = :id'), {'id': tool_id}); conn.commit()
    return jsonify({'success': True})

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    with engine.connect() as conn:
        try:
            prompts = conn.execute(text('SELECT * FROM prompts ORDER BY category, title ASC')).fetchall()
            return jsonify([dict(p._mapping) for p in prompts])
        except Exception:
            return jsonify([])

@app.route('/api/prompts/add', methods=['POST'])
def add_prompt():
    if not engine: return jsonify({"error": "Database not configured"}), 500
    data = request.json; date_added_str = datetime.now()
    with engine.connect() as conn:
        conn.execute(text('INSERT INTO prompts (title, category, prompt_text, notes, date_added) VALUES (:title, :category, :prompt_text, :notes, :date_added)'),{'title': data['title'], 'category': data['category'], 'prompt_text': data['prompt_text'], 'notes': data.get('notes', ''), 'date_added': date_added_str}); conn.commit()
    return jsonify({'success': True}), 201

# --- INICIA O SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=(not IS_PRODUCTION), host='0.0.0.0', port=port)