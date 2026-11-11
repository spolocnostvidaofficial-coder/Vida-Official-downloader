import os
import json
from datetime import datetime
from math import ceil
from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "vida_official_super_secret_key_2026"

UPLOAD_FOLDER = 'vidamovie_storage'
DATA_FILE = 'database.json'

if os.path.exists(DATA_FILE):
    try:
        os.remove(DATA_FILE)
    except Exception:
        pass

initial_data = {
    'users': {
        'sebastianzettl': {
            'password': 'Se10102006',
            'email': 'sebastianzettl4@gmail.com',
            'hobby': 'Admin'
        }
    },
    'metadata': {},
    'coins': {'sebastianzettl': 999999999},
    'banned': {},
    'vip': {'sebastianzettl': True},
    'reports': [],
    'messages': {},
    'agreements': {'sebastianzettl': 'Áno, súhlasil'},
    'recovery': {}
}

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(initial_data, f, ensure_ascii=False, indent=4)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Zabezpečenie: admin má vždy nekonečno (obrovské číslo, ktoré sa nikdy neminie)
                if 'coins' not in data:
                    data['coins'] = {}
                data['coins']['sebastianzettl'] = 999999999
                return data
            except json.JSONDecodeError:
                return {'users': {}, 'metadata': {}, 'coins': {'sebastianzettl': 999999999}, 'banned': {}, 'vip': {}, 'reports': [], 'messages': {}, 'agreements': {}, 'recovery': {}}
    return {'users': {}, 'metadata': {}, 'coins': {'sebastianzettl': 999999999}, 'banned': {}, 'vip': {}, 'reports': [], 'messages': {}, 'agreements': {}, 'recovery': {}}

def save_data(data):
    # Vždy pred uložením uistíme, že admin má maximálny počet coinov
    if 'coins' not in data:
        data['coins'] = {}
    data['coins']['sebastianzettl'] = 999999999
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_valid_name(name):
    name = name.strip()
    if len(name) < 3:
        return False
    gibberish = ['gdjdj', 'asdf', 'qwer', 'zxcv', 'asdfgh', 'hjkl', 'ytrfdsa', 'esfygr', 'esfyg', 'aaaa', 'ffff', 'hdeuh', 'halabala']
    if name.lower() in gibberish:
        return False
    if len(set(name.lower())) <= 2:
        return False
    vowels = "aáeéiíoóuúýôäaeiouy"
    return any(char in vowels for char in name.lower())

def format_file_size(size_bytes):
    if size_bytes == 0:
        return "0 KB"
    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{round(size_kb, 2)} KB"
    size_mb = size_kb / 1024
    if size_mb < 1024:
        return f"{round(size_mb, 2)} MB"
    size_gb = size_mb / 1024
    return f"{round(size_gb, 2)} GB"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Vida Official</title>
    <style>
        #splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #000000;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: opacity 1s ease;
        }

        .splash-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            animation: zoomInLogo 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
        }

        @keyframes zoomInLogo {
            0% { transform: scale(0.6); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }

        .neon-circle {
            width: 120px;
            height: 120px;
            border: 4px solid #38bdf8;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0 25px #38bdf8, 0 0 50px rgba(56, 189, 248, 0.5), inset 0 0 15px #38bdf8;
            background: #000000;
            padding: 10px;
            text-align: center;
        }

        .neon-circle .brand-text {
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            font-family: sans-serif;
            text-shadow: 
                0 0 4px #38bdf8, 
                0 0 8px #38bdf8, 
                0 0 15px #38bdf8,
                0 0 25px #38bdf8;
            letter-spacing: 0.5px;
        }

        .splash-loading-text {
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            margin-top: 15px;
            font-family: sans-serif;
            text-shadow: 0 0 8px #38bdf8;
        }

        .loading-dots {
            display: flex;
            gap: 6px;
            margin-top: 12px;
        }

        .loading-dots span {
            width: 8px;
            height: 8px;
            background-color: #38bdf8;
            border-radius: 50%;
            box-shadow: 0 0 8px #38bdf8;
            animation: bounceDots 1.2s infinite ease-in-out;
        }

        .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
        .loading-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounceDots {
            0%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-8px); }
        }

        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #ffffff; color: #111827; margin: 0; padding: 0; }
        
        header { 
            background: #ffffff; 
            padding: 15px 30px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            border-bottom: 1px solid #e5e7eb; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.02); 
        }
        .header-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
        .btn-auth { background: #f3f4f6; color: #374151; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px; border: 1px solid #d1d5db; }
        .btn-vip { background: #dc2626; color: white; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px; }
        .header-right { display: flex; align-items: center; gap: 15px; }
        
        .logo { 
            display: inline-flex; 
            align-items: center; 
            justify-content: center; 
            width: 44px; 
            height: 44px; 
            background: #000000; 
            border: 3px solid #38bdf8; 
            border-radius: 50%; 
            color: #ffffff; 
            font-weight: bold; 
            font-size: 20px; 
            text-decoration: none; 
            box-shadow: 0 0 12px #38bdf8, inset 0 0 6px #38bdf8; 
            text-shadow: 0 0 6px #38bdf8;
            cursor: pointer;
        }
        
        .coin-badge {
            display: inline-flex; align-items: center; justify-content: center;
            width: 32px; height: 32px; background: #000000; border: 3px solid #38bdf8;
            border-radius: 50%; color: #ffffff; font-weight: bold; font-size: 16px;
            box-shadow: 0 0 12px #38bdf8, inset 0 0 8px #38bdf8;
            margin-right: 8px; vertical-align: middle;
            text-shadow: 0 0 6px #38bdf8;
        }

        .menu-container { position: relative; display: inline-block; }
        .menu-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: #374151; padding: 0 5px; font-weight: bold; }
        .menu-dropdown { display: none; position: absolute; right: 0; top: 30px; background: white; min-width: 220px; box-shadow: 0px 8px 16px rgba(0,0,0,0.1); border-radius: 6px; border: 1px solid #e5e7eb; z-index: 10; }
        .menu-dropdown a { color: #374151; padding: 10px 14px; text-decoration: none; display: block; font-size: 13px; font-weight: 500; display: flex; align-items: center; }
        .menu-dropdown a:hover { background: #f3f4f6; color: #dc2626; }
        .menu-container:hover .menu-dropdown { display: block; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .search-box-container { text-align: center; margin-bottom: 25px; }
        .search-input { width: 50% !important; display: inline-block !important; padding: 10px !important; border-radius: 20px !important; text-align: center; border: 1px solid #d1d5db; }
        .card { background: #ffffff; border: 1px solid #e5e7eb; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        .card h3 { margin-top: 0; color: #111827; border-bottom: 1px solid #f3f4f6; padding-bottom: 10px; font-size: 16px; }
        input, select, textarea { background: #f9fafb; border: 1px solid #d1d5db; color: #111827; padding: 10px; border-radius: 6px; width: 100%; box-sizing: border-box; margin-bottom: 10px; font-size: 14px; }
        .btn-primary { background: #dc2626; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; text-decoration: none; font-weight: 600; display: inline-block; font-size: 14px; }
        .btn-primary:hover { background: #b91c1c; }
        .btn-danger { background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; padding: 6px 10px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 12px; }
        .btn-download-link { background: #16a34a; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 12px; }
        ul { list-style-type: none; padding: 0; margin: 0; }
        li { background: #f9fafb; border: 1px solid #e5e7eb; padding: 12px 15px; margin-bottom: 8px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; }
        .file-info { display: flex; flex-direction: column; }
        .file-name { font-weight: 600; font-size: 14px; color: #111827; text-decoration: none; }
        .file-meta { font-size: 11px; color: #6b7280; margin-top: 2px; }
        .actions { display: flex; gap: 8px; align-items: center; }
        
        #upload-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; justify-content: center; align-items: center; color: white; flex-direction: column; font-family: sans-serif; }
        .progress-box { background: white; color: #111827; padding: 30px; border-radius: 10px; width: 350px; text-align: center; }
        .progress-bar-container { width: 100%; background: #e5e7eb; border-radius: 6px; overflow: hidden; margin-top: 15px; height: 20px; }
        .progress-bar { width: 0%; height: 100%; background: #dc2626; transition: width 0.1s linear; }

        .admin-msg-box { background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px; border-radius: 6px; margin-bottom: 20px; color: #1e40af; font-weight: 500; }
        .warning-notice { background: #fef3c7; border: 1px solid #f59e0b; padding: 12px; border-radius: 6px; margin-bottom: 15px; color: #92400e; font-size: 13px; font-weight: 600; }

        @media (max-width: 768px) {
            header { padding: 12px 15px; flex-direction: column; gap: 12px; align-items: stretch; }
            .header-left { justify-content: space-between; width: 100%; }
            .header-right { justify-content: space-between; width: 100%; border-top: 1px solid #f3f4f6; padding-top: 10px; }
        }
    </style>
</head>
<body>
    <!-- Úvodná obrazovka (10 sekúnd iba pri prvom vstupe) -->
    <div id="splash-screen">
        <div class="splash-content">
            <div class="neon-circle">
                <span class="brand-text">Vida Official</span>
            </div>
            <div class="splash-loading-text">Načítava sa...</div>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </div>

    <script>
        window.addEventListener('load', () => {
            if (sessionStorage.getItem('vida_loaded')) {
                const splash = document.getElementById('splash-screen');
                if (splash) splash.style.display = 'none';
            } else {
                setTimeout(() => {
                    const splash = document.getElementById('splash-screen');
                    if (splash) {
                        splash.style.opacity = '0';
                        setTimeout(() => { splash.style.display = 'none'; }, 1000);
                    }
                    sessionStorage.setItem('vida_loaded', 'true');
                }, 10000);
            }
        });
    </script>

    <header>
        <div class="header-left">
            {% if 'user' in session %}
                <span style="font-weight: 600; font-size: 14px; color: #374151;">👤 {{ session['user'] }}</span>
                <a href="/logout" class="btn-auth">Odhlásiť</a>
            {% else %}
                <a href="/login" class="btn-auth">Prihlásiť sa</a>
                <a href="/register" class="btn-auth">Registrácia</a>
            {% endif %}
            <a href="#" class="btn-vip" onclick="alert('VIP predplatné'); return false;">⭐ VIP</a>
        </div>
        <div class="header-right">
            <!-- Klikateľné logo s veľkým V v strede a neónovými okrajmi -->
            <a href="/" class="logo" title="Vida Official">V</a>
            <div class="menu-container">
                <button class="menu-btn">⋮</button>
                <div class="menu-dropdown">
                    <a href="/">🏠 Domov</a>
                    {% if 'user' in session %}
                        <a href="/my-coins"><span class="coin-badge">V</span>Moje coiny</a>
                        {% if is_admin %}
                            <a href="/admin-panel" style="color: #dc2626; font-weight: bold;">🛡️ Admin Panel (Správa ľudí)</a>
                        {% endif %}
                    {% endif %}
                    <a href="#" onclick="alert('Stiahnutie mobilnej aplikácie'); return false;">📥 Stiahnuť aplikáciu</a>
                </div>
            </div>
        </div>
    </header>
    <div class="container">
        
        {% if error %}
            <div style="background: #fee2e2; border: 1px solid #fca5a5; color: #dc2626; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-weight: 600; text-align: center;">
                ⚠️ {{ error }}
            </div>
        {% endif %}

        {% if admin_message %}
            <div class="admin-msg-box">
                📬 <strong>Správa od majiteľa / admina:</strong> {{ admin_message }}
            </div>
        {% endif %}

        <div class="search-box-container">
            <form method="get" action="/">
                <input type="text" name="q" class="search-input" value="{{ search_query }}" placeholder="🔍 Hľadať video, súbor, short, obrázok...">
            </form>
        </div>

        <div class="card" style="border-top: 4px solid #dc2626;">
            <h3>📤 Pridať nové video, súbor alebo obsah</h3>
            <div class="warning-notice">
                ⚠️ Upozornenie: Musíte nahrať **vlastné videá a súbory**! Inak budú natrvalo odstránené.
            </div>
            {% if 'user' in session %}
                <form id="upload-form" action="/upload" method="post" enctype="multipart/form-data" onsubmit="startUpload(event)">
                    <label style="font-weight:600; font-size:13px; display:block; margin-bottom:5px;">1. Zvoľte kategóriu obsahu:</label>
                    <select name="category" id="category-select" required>
                        <option value="Video">📹 Video</option>
                        <option value="Short">⚡ Short (originál max 60 sekúnd)</option>
                        <option value="Hudba">🎵 Hudba</option>
                        <option value="Obrázok">🖼️ Obrázok</option>
                        <option value="Súbor">📁 Všeobecný súbor</option>
                    </select>
                    
                    <label style="font-weight:600; font-size:13px; display:block; margin-bottom:5px;">2. Zadajte názov:</label>
                    <input type="text" name="title" placeholder="Názov obsahu..." required>

                    <label style="font-weight:600; font-size:13px; display:block; margin-bottom:5px;">3. Vyberte vlastný súbor / video:</label>
                    <input type="file" name="movie" id="movie-file" required>
                    
                    <select name="age_rating">
                        <option value="Vhodné od 4 rokov (4+)">Vhodné od 4 rokov (4+)</option>
                        <option value="Vhodné od 18 rokov (18+)">Nevhodné pre mladších ako 18 rokov (18+)</option>
                    </select>

                    <select name="kids">
                        <option value="Určené pre deti">Určené pre deti</option>
                        <option value="Nevhodné pre deti">Nevhodné pre deti</option>
                    </select>

                    <button type="submit" class="btn-primary">Spracovať, overiť a nahrať</button>
                </form>
            {% else %}
                <p style="text-align: center; color: #6b7280; margin: 15px 0;">Pre pridávanie súborov sa musíte najprv <a href="/login" style="color: #dc2626; font-weight: bold;">prihlásiť</a>.</p>
            {% endif %}
        </div>

        <div class="card">
            <h3>📁 Trvalo dostupné videá, súbory a médiá (Všetko je viditeľné)</h3>
            {% if files %}
                <ul>
                    {% for file in files %}
                        <li>
                            <div class="file-info">
                                <a class="file-name" href="/detail/{{ file.real_filename }}">🎞️ {{ file.display_name }} [{{ file.category }}]</a>
                                <span class="file-meta">Dátum: {{ file.upload_date }} | Autor: {{ file.uploader }} | Veľkosť: {{ file.size_formatted }} | Súbor: {{ file.real_filename }}</span>
                            </div>
                            <div class="actions">
                                <a class="btn-download-link" href="/download/{{ file.real_filename }}">📥 Stiahnuť</a>
                                <a class="btn-auth" style="padding: 6px 10px; font-size: 12px;" href="/detail/{{ file.real_filename }}">Detail</a>
                                {% if 'user' in session %}
                                    <a href="/report-page/{{ file.real_filename }}" style="background:#eab308; color:white; padding:6px 10px; border-radius:6px; text-decoration:none; font-weight:600; font-size:12px;">🚩 Nahlásiť</a>
                                {% endif %}
                                {% if session.get('user') == file.uploader or is_admin %}
                                    <a class="btn-danger" href="/delete/{{ file.real_filename }}" onclick="return confirm('Naozaj vymazať?')">🗑️ Kôš</a>
                                {% endif %}
                            </div>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p style="color: #6b7280; text-align: center; padding: 15px 0;">Žiadne súbory.</p>
            {% endif %}
        </div>
    </div>

    <div id="upload-overlay">
        <div class="progress-box">
            <h3 id="progress-status" style="margin-top:0; color:#dc2626;">Prebieha overovanie obsahu...</h3>
            <p id="progress-text" style="font-size:13px; color:#4b5563; margin:5px 0;">Kontroluje sa, či ide o vlastné video/súbor...</p>
            <div class="progress-bar-container">
                <div id="progress-bar" class="progress-bar"></div>
            </div>
            <p id="progress-percent" style="font-weight:bold; margin-top:10px; color:#111827;">0%</p>
        </div>
    </div>

    <script>
        function startUpload(event) {
            event.preventDefault();
            const form = document.getElementById('upload-form');
            const fileInput = document.getElementById('movie-file');
            
            if (fileInput.files.length === 0) {
                alert("Prosím, vyberte súbor!");
                return;
            }

            const overlay = document.getElementById('upload-overlay');
            const statusTitle = document.getElementById('progress-status');
            const statusText = document.getElementById('progress-text');
            const progressBar = document.getElementById('progress-bar');
            const progressPercent = document.getElementById('progress-percent');
            
            overlay.style.display = 'flex';
            let progress = 0;
            
            let interval = setInterval(() => {
                progress += 5;
                if (progress <= 90) {
                    progressBar.style.width = progress + '%';
                    progressPercent.innerText = progress + '%';
                }
            }, 50);

            const formData = new FormData(form);

            fetch('/upload', {
                method: 'POST',
                body: formData
            }).then(response => {
                clearInterval(interval);
                progressBar.style.width = '100%';
                progressPercent.innerText = '100%';
                statusTitle.innerText = "Dokončené!";
                statusText.innerText = "Súbor úspešne pridaný.";
                
                setTimeout(() => {
                    window.location.href = '/';
                }, 400);
            }).catch(error => {
                clearInterval(interval);
                overlay.style.display = 'none';
                alert("Chyba pri nahrávaní súboru.");
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    error = request.args.get('error', '')
    data = load_data()
    search_query = request.args.get('q', '').lower()
    
    current_user = session.get('user', '')
    user_info = data.get('users', {}).get(current_user, {})
    is_admin = (current_user == "sebastianzettl" or user_info.get('email') == "sebastianzettl4@gmail.com")

    if current_user in data.get('banned', {}):
        ban_info = data['banned'][current_user]
        return f"<body style='font-family:sans-serif; text-align:center; padding:50px;'><h2>⛔ Majiteľ vás zablokoval z dôvodu porušenia pravidiel.</h2><p>Trvanie blokovania: {ban_info}</p><br><a href='/logout'>Odhlásiť sa</a></body>"

    admin_message = data.get('messages', {}).get(current_user, '')

    all_files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
    file_list = []
    for f in all_files:
        meta = data['metadata'].get(f, {'display_name': f, 'upload_date': 'Neznámy', 'uploader': 'Neznámy', 'category': 'Video'})
        if search_query in f.lower() or search_query in meta['display_name'].lower() or search_query in meta['uploader'].lower():
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f)
            size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            meta['real_filename'] = f
            meta['size_formatted'] = format_file_size(size_bytes)
            file_list.append(meta)

    return render_template_string(HTML_TEMPLATE, files=file_list, search_query=search_query, error=error, is_admin=is_admin, admin_message=admin_message)

@app.route('/my-coins')
def my_coins():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    user = session['user']
    
    is_admin = (user == "sebastianzettl" or data.get('users', {}).get(user, {}).get('email') == "sebastianzettl4@gmail.com")
    
    # Pre admina symbol nekonečna, pre ostatných ich reálny stav coinov
    if is_admin:
        coins_display = "∞"
    else:
        coins_display = str(data.get('coins', {}).get(user, 0))
    
    return f'''
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8"><title>Moje coiny</title>
        <style>
            body {{ font-family: sans-serif; background: #f9fafb; padding: 40px; text-align: center; }}
            .coin-box {{ max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            /* Neónový kruh s veľkým V v strede – presne ako logo, žiadne žlté mince */
            .neon-v-badge {{
                display: inline-flex; align-items: center; justify-content: center;
                width: 90px; height: 90px; background: #000000; border: 4px solid #38bdf8;
                border-radius: 50%; color: #ffffff; font-weight: bold; font-size: 42px;
                box-shadow: 0 0 25px #38bdf8, 0 0 50px rgba(56, 189, 248, 0.4), inset 0 0 12px #38bdf8;
                text-shadow: 0 0 8px #38bdf8, 0 0 15px #38bdf8;
                margin-bottom: 15px;
            }}
            h2 {{ color: #111827; margin-bottom: 5px; }}
            p {{ font-size: 38px; font-weight: bold; color: #111827; text-shadow: 0 0 5px rgba(56, 189, 248, 0.3); }}
            .btn-back {{ background: #dc2626; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 15px; box-shadow: 0 0 8px rgba(220, 38, 38, 0.4); }}
            .btn-back:hover {{ background: #b91c1c; }}
        </style>
    </head>
    <body>
        <div class="coin-box">
            <div class="neon-v-badge">V</div>
            <h2>Moje Coiny</h2>
            <p>{coins_display}</p>
            <br><a href="/" class="btn-back">Späť domov</a>
        </div>
    </body>
    </html>
    '''

@app.route('/report-page/<filename>', methods=['GET', 'POST'])
def report_page(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    data = load_data()
    meta = data['metadata'].get(filename, {'display_name': filename, 'category': 'Súbor', 'uploader': 'Neznámy'})
    
    if request.method == 'POST':
        reporter_email = request.form.get('reporter_email', '').strip()
        reason = request.form.get('reason', '').strip()
        
        if 'reports' not in data:
            data['reports'] = []
            
        reporter = session['user']
        report_entry = {
            'id': len(data['reports']) + 1,
            'reporter': reporter,
            'reporter_email': reporter_email,
            'target_user': meta['uploader'],
            'details': f"Nahlásený súbor: '{filename}' | Názov: '{meta['display_name']}' | Autor: {meta['uploader']} | Dôvod: {reason}",
            'date': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        data['reports'].append(report_entry)
        save_data(data)
        
        return """
        <body style="font-family:sans-serif; text-align:center; padding:50px;">
            <h2>✅ Hlásenie bolo úspešne odoslané adminovi</h2>
            <p>Admin vám pošle vyjadrenie na váš e-mail.</p>
            <br><a href="/" style="background:#dc2626; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Späť domov</a>
        </body>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="sk">
    <head><meta charset="UTF-8"><title>Nahlásiť obsah</title></head>
    <body style="font-family:sans-serif; background:#f9fafb; padding:40px; text-align:center;">
        <div style="max-width:450px; margin:auto; background:white; padding:30px; border-radius:10px; border:1px solid #e5e7eb;">
            <h2>🚩 Nahlásiť nevyhovujúci obsah</h2>
            <p style="text-align:left; font-size:13px; color:#374151; background:#f3f4f6; padding:10px; border-radius:6px;">
                <strong>Súbor:</strong> {filename}<br>
                <strong>Názov:</strong> {meta['display_name']}<br>
                <strong>Autor:</strong> {meta['uploader']}
            </p>
            <form method="post">
                <input type="email" name="reporter_email" placeholder="Váš e-mail..." required style="padding:10px; width:100%; margin-bottom:10px;">
                <textarea name="reason" placeholder="Dôvod (napr. nie je to vlastné video/súbor)..." required style="padding:10px; width:100%; margin-bottom:10px;"></textarea>
                <button type="submit" style="background:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; width:100%;">Odoslať hlásenie</button>
            </form>
            <br><a href="/" style="color:#6b7280; text-decoration:none;">← Zrušiť a späť domov</a>
        </div>
    </body>
    </html>
    """

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    data = load_data()
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'request':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            forgot_type = request.form.get('forgot_type', 'heslo')
            hobby = request.form.get('hobby', '').strip()
            details = request.form.get('details', '').strip()
            
            if not username:
                username = "Neznámy_" + email

            if 'recovery' not in data:
                data['recovery'] = {}
            data['recovery'][username] = {
                'email': email,
                'forgot_type': forgot_type,
                'hobby': hobby,
                'details': details,
                'status': 'Čaká na schválenie',
                'code': ''
            }
            save_data(data)
            msg = f"Žiadosť bola odoslaná na e-mail: {email}."
            
        elif action == 'verify':
            username = request.form.get('username', '').strip()
            code = request.form.get('code', '').strip()
            rec = data.get('recovery', {}).get(username, {})
            if rec.get('code') == code:
                forgot_type = rec.get('forgot_type', 'heslo')
                change_fields = ""
                if forgot_type == 'heslo':
                    change_fields = '<input type="password" name="new_password" placeholder="Nové heslo..." required style="padding:10px; width:100%; margin-bottom:10px;">'
                elif forgot_type == 'email':
                    change_fields = '<input type="email" name="new_email" placeholder="Nový e-mail..." required style="padding:10px; width:100%; margin-bottom:10px;">'
                elif forgot_type == 'meno':
                    change_fields = '<input type="text" name="new_username" placeholder="Nové meno..." required style="padding:10px; width:100%; margin-bottom:10px;">'

                return f"""
                <!DOCTYPE html>
                <html lang="sk">
                <head><meta charset="UTF-8"><title>Zmena údajov</title></head>
                <body style="font-family:sans-serif; background:#f9fafb; padding:40px; text-align:center;">
                    <div style="max-width:450px; margin:auto; background:white; padding:30px; border-radius:10px; border:1px solid #e5e7eb;">
                        <h2 style="color:#16a34a;">✅ Kód je správny!</h2>
                        <form method="post" action="/update-credential">
                            <input type="hidden" name="username" value="{username}">
                            <input type="hidden" name="forgot_type" value="{forgot_type}">
                            {change_fields}
                            <button type="submit" style="background:#16a34a; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; width:100%;">Uložiť</button>
                        </form>
                    </div>
                </body>
                </html>
                """
            else:
                msg = "❌ Nesprávny kód."

    return f"""
    <!DOCTYPE html>
    <html lang="sk">
    <head><meta charset="UTF-8"><title>Obnovenie prístupu</title></head>
    <body style="font-family:sans-serif; background:#f9fafb; padding:40px; text-align:center;">
        <div style="max-width:450px; margin:auto; background:white; padding:30px; border-radius:10px; border:1px solid #e5e7eb;">
            <h2>Zabudli ste prístup?</h2>
            {f'<p style="color:green; font-weight:bold;">{msg}</p>' if msg else ''}
            <form method="post" style="margin-bottom:20px;">
                <select name="forgot_type" id="forgot-type-select" style="padding:10px; width:100%; margin-bottom:10px;">
                    <option value="heslo">🔑 Heslo</option>
                    <option value="email">📧 E-mail</option>
                    <option value="meno">👤 Meno</option>
                </select>
                <input type="text" name="username" id="user-identifier-input" placeholder="Meno vášho účtu..." required style="padding:10px; width:100%; margin-bottom:10px;">
                <input type="email" name="email" placeholder="Váš e-mail..." required style="padding:10px; width:100%; margin-bottom:10px;">
                <input type="text" name="hobby" placeholder="Obľúbená záľuba..." required style="padding:10px; width:100%; margin-bottom:10px;">
                <textarea name="details" placeholder="Popíšte problém..." required style="padding:10px; width:100%; margin-bottom:10px;"></textarea>
                <button type="submit" name="action" value="request" style="background:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; width:100%;">Odoslať žiadosť</button>
            </form>
            <hr style="border:0; border-top:1px solid #e5e7eb; margin:20px 0;">
            <h3>Zadať 6-miestny kód</h3>
            <form method="post">
                <input type="hidden" name="action" value="verify">
                <input type="text" name="username" id="verify-user-input" placeholder="Meno účtu..." required style="padding:10px; width:100%; margin-bottom:10px;">
                <input type="text" name="code" placeholder="6-miestny kód" maxlength="6" required style="padding:10px; width:100%; margin-bottom:10px; text-align:center; font-size:18px; letter-spacing:4px;">
                <button type="submit" style="background:#16a34a; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; width:100%;">Overiť</button>
            </form>
            <br><a href="/login" style="color:#dc2626; text-decoration:none; font-weight:bold;">← Späť na prihlásenie</a>
        </div>
    </body>
    </html>
    """

@app.route('/update-credential', methods=['POST'])
def update_credential():
    username = request.form.get('username')
    forgot_type = request.form.get('forgot_type')
    data = load_data()
    
    if username in data['users']:
        if forgot_type == 'heslo':
            data['users'][username]['password'] = request.form.get('new_password')
        elif forgot_type == 'email':
            data['users'][username]['email'] = request.form.get('new_email')
        elif forgot_type == 'meno':
            new_username = request.form.get('new_username').strip()
            if new_username and new_username not in data['users']:
                data['users'][new_username] = data['users'].pop(username)
                if username in data.get('coins', {}):
                    data['coins'][new_username] = data['coins'].pop(username)
                username = new_username
        save_data(data)
        session['user'] = username
        return redirect(url_for('index'))
    return "<body style='font-family:sans-serif; text-align:center; padding:50px;'><h2>❌ Účet sa nenašiel.</h2><a href='/login'>Späť</a></body>"

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    current_user = session.get('user', '')
    data = load_data()
    user_info = data.get('users', {}).get(current_user, {})
    is_admin = (current_user == "sebastianzettl" or user_info.get('email') == "sebastianzettl4@gmail.com")

    if 'user' not in session or not is_admin:
        return redirect(url_for('index'))
    
    q = request.args.get('q', '').lower()

    if request.method == 'POST':
        target_user = request.form.get('target_user')
        action = request.form.get('action')
        
        if action == 'ban':
            value = request.form.get('value')
            unit = request.form.get('unit')
            data['banned'][target_user] = f"{value} {unit}"
            save_data(data)
        elif action == 'unban':
            if target_user in data.get('banned', {}):
                del data['banned'][target_user]
                save_data(data)
        elif action == 'delete_user':
            if target_user in data['users']:
                del data['users'][target_user]
                save_data(data)
        elif action == 'toggle_vip':
            is_vip = data.get('vip', {}).get(target_user, False)
            if 'vip' not in data:
                data['vip'] = {}
            data['vip'][target_user] = not is_vip
            save_data(data)
        elif action == 'edit_user':
            new_username = request.form.get('new_username', '').strip()
            if new_username and new_username not in data['users']:
                data['users'][new_username] = data['users'].pop(target_user)
                if target_user in data.get('coins', {}):
                    data['coins'][new_username] = data['coins'].pop(target_user)
                save_data(data)
        elif action == 'give_coins':
            amount = int(request.form.get('coin_amount', 100))
            if 'coins' not in data:
                data['coins'] = {}
            data['coins'][target_user] = data['coins'].get(target_user, 0) + amount
            save_data(data)
        elif action == 'clear_reports':
            data['reports'] = []
            save_data(data)

        return redirect(url_for('admin_panel'))

    users_html = ""
    for u, info in data.get('users', {}).items():
        if q and q not in u.lower():
            continue
        is_banned = u in data.get('banned', {})
        status = f"🔴 Zablokovaný ({data['banned'][u]})" if is_banned else "🟢 Aktívny"
        
        # Zobrazenie nekonečna pre admina, pre ostatných ich reálne coiny
        coins = "∞" if (u == "sebastianzettl" or info.get('email') == "sebastianzettl4@gmail.com") else data.get('coins', {}).get(u, 0)
        hobby = info.get('hobby', 'Nezadaná')

        users_html += f"""
        <li style="background:white; padding:15px; margin-bottom:12px; border-radius:6px; border:1px solid #e5e7eb; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <span><strong>👤 {u}</strong> | E-mail: {info.get('email')} | Coiny: {coins} 🪙 - {status}</span>
            <div style="display:flex; gap:5px; align-items:center;">
                <form method="post" style="display:flex; gap:5px; margin:0;">
                    <input type="hidden" name="target_user" value="{u}">
                    <input type="number" name="coin_amount" value="500" style="width:70px; padding:4px; font-size:12px;" placeholder="Počet">
                    <button type="submit" name="action" value="give_coins" style="background:#16a34a; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; font-size:12px;">💰 Poslať coiny</button>
                </form>
                <form method="post" style="margin:0;">
                    <input type="hidden" name="target_user" value="{u}">
                    <button type="submit" name="action" value="delete_user" style="background:#374151; color:white; border:none; padding:5px 8px; border-radius:4px; cursor:pointer; font-size:12px;" onclick="return confirm('Vymazať?')">🗑️ Zmazať</button>
                </form>
            </div>
        </li>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="sk">
    <head><meta charset="UTF-8"><title>Admin Panel</title></head>
    <body style="font-family:sans-serif; background:#f9fafb; padding:40px;">
        <div style="max-width:950px; margin:auto;">
            <h2>🛡️ Admin Panel - Vida Official (Správa Coiny)</h2>
            <p><a href="/" style="color:#dc2626; text-decoration:none; font-weight:bold;">← Späť na domov</a></p>
            <ul style="list-style:none; padding:0;">{users_html}</ul>
        </div>
    </body>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    if not is_valid_name(title):
        return redirect(url_for('index', error="⚠️ Názov obsahu obsahuje nepovolené alebo náhodné znaky (napr. 'halabala'). Zadajte platný názov!"))

    uploader = session['user']
    upload_date = datetime.now().strftime('%d.%m.%Y %H:%M')
    data = load_data()

    if 'movie' in request.files:
        file = request.files['movie']
        if file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            data['metadata'][filename] = {
                'display_name': title,
                'upload_date': upload_date,
                'uploader': uploader,
                'category': request.form.get('category', 'Video')
            }
            save_data(data)
            
    return redirect(url_for('index'))

@app.route('/detail/<filename>')
def detail_file(filename):
    data = load_data()
    meta = data['metadata'].get(filename, {'display_name': filename, 'upload_date': 'Neznámy', 'uploader': 'Neznámy', 'category': 'Video'})
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    size_formatted = format_file_size(size_bytes)

    return f"""
    <!DOCTYPE html>
    <html lang="sk">
    <head><meta charset="UTF-8"><title>Detail</title></head>
    <body style="font-family:sans-serif; padding:40px; background:#fff;">
        <div style="max-width:600px; margin:auto; background:#f9fafb; padding:30px; border:1px solid #e5e7eb; border-radius:10px;">
            <h2 style="color:#dc2626;">🎞️ {meta['display_name']}</h2>
            <p><strong>Autor:</strong> {meta['uploader']}</p>
            <p><strong>Veľkosť:</strong> {size_formatted}</p>
            <br><a href="/download/{filename}" style="background:#dc2626; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">📥 Stiahnuť súbor</a>
            <br><br><a href="/" style="color:#6b7280; text-decoration:none;">← Späť domov</a>
        </div>
    </body>
    """

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    current_user = session['user']
    user_info = data.get('users', {}).get(current_user, {})
    is_admin = (current_user == "sebastianzettl" or user_info.get('email') == "sebastianzettl4@gmail.com")
    meta = data['metadata'].get(filename, {})
    
    if current_user == meta.get('uploader') or is_admin:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        if filename in data['metadata']:
            del data['metadata'][filename]
            save_data(data)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        email = request.form.get('email', '').strip()
        hobby = request.form.get('hobby', '').strip()
        agreement = request.form.get('agreement')
        
        if not agreement:
            return '''<body style="font-family:sans-serif; background:#fff; padding:40px; text-align:center;">
                    <h2>⚠️ Musíte potvrdiť pravidlá a povinnosť nahrávať iba vlastné videá a súbory!</h2>
                    <br><a href="/register" style="color:#dc2626; font-weight:bold;">Znova</a>
                    </body>'''

        if not is_valid_name(username):
            return '''<body style="font-family:sans-serif; background:#fff; padding:40px; text-align:center;">
                    <h2>⚠️ Zvolené meno používateľa obsahuje nepovolené alebo náhodné znaky (napr. 'halabala')!</h2>
                    <br><a href="/register" style="color:#dc2626; font-weight:bold;">Skúsiť iné meno</a>
                    </body>'''

        data = load_data()
        
        if email == "sebastianzettl4@gmail.com":
            username = "sebastianzettl"

        if username in data['users']:
            msg = "⚠️ Už máte účet!"
        else:
            for u, info in data['users'].items():
                if info.get('email') == email:
                    msg = "⚠️ Už máte účet!"
                    break

        if msg:
            return f'''
            <!DOCTYPE html>
            <html lang="sk">
            <head><meta charset="UTF-8"><title>Už máte účet</title></head>
            <body style="font-family:sans-serif; background:#fff; padding:40px; text-align:center;">
                <h2 style="color:#dc2626;">{msg}</h2>
                <p>Už ste zaregistrovaní, môžete sa prihlásiť!</p>
                <br><a href="/login" style="background:#dc2626; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Prejsť na prihlásenie</a>
            </body>
            </html>
            '''

        data['users'][username] = {'password': password, 'email': email, 'hobby': hobby}
        if 'coins' not in data:
            data['coins'] = {}
        data['coins'][username] = 0
        if 'agreements' not in data:
            data['agreements'] = {}
        data['agreements'][username] = "Áno, súhlasil"
        
        save_data(data)
        
        return '''
        <!DOCTYPE html>
        <html lang="sk">
        <head><meta charset="UTF-8"><title>Registrácia úspešná</title></head>
        <body style="font-family:sans-serif; background:#f9fafb; padding:40px; text-align:center;">
            <div style="max-width:400px; margin:auto; background:white; padding:30px; border-radius:10px; border:1px solid #e5e7eb;">
                <h2 style="color:#16a34a;">✅ Registrácia prebehla úspešne!</h2>
                <p style="font-weight:bold; color:#374151; margin:15px 0;">Už ste zaregistrovaní, môžete sa prihlásiť!</p>
                <br><a href="/login" style="background:#dc2626; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Prihlásiť sa</a>
            </div>
        </body>
        </html>
        '''

    return '''<body style="font-family:sans-serif; background:#f9fafb; padding:40px;">
              <div style="max-width:400px; margin:auto; background:white; padding:30px; border-radius:10px; border:1px solid #e5e7eb;">
              <h2>Registrácia do Vida Official</h2>
              <div style="background:#f3f4f6; padding:12px; font-size:12px; margin-bottom:15px; border-radius:6px; color:#4b5563;">
                  <strong>ℹ️ Pravidlo:</strong> Je nutné nahrať iba <strong>vlastné videá a súbory</strong>, inak budú odstránené.
              </div>
              <form method="post">
              <input type="text" name="username" placeholder="Meno" required style="width:100%; padding:10px; margin-bottom:10px;"><br>
              <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin-bottom:10px;"><br>
              <input type="text" name="hobby" placeholder="Obľúbená záľuba..." required style="width:100%; padding:10px; margin-bottom:10px;"><br>
              <input type="password" name="password" placeholder="Heslo" required style="width:100%; padding:10px; margin-bottom:10px;"><br>
              <label style="font-size:13px; display:flex; align-items:center; gap:8px; margin-bottom:15px;">
                  <input type="checkbox" name="agreement" value="yes" required style="width:auto; margin:0;">
                  Súhlasím s pravidlami a budem nahrávať iba vlastné videá a súbory.
              </label>
              <button type="submit" style="background:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; width:100%;">Zaregistrovať sa</button>
              </form><br><div style="text-align:center;"><a href="/">Domov</a> | <a href="/login">Prihlásiť sa</a></div></div></body>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        data = load_data()
        
        user_exists = False
        if username in data['users']:
            user_exists = True
            if data['users'][username]['password'] == password:
                session['user'] = username
                return '''
                <!DOCTYPE html>
                <html lang="sk">
                <head>
                    <meta charset="UTF-8">
                    <title>Prihlasovanie...</title>
                    <style>
                        body { background: #000000; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; }
                        .neon-circle {
                            width: 120px; height: 120px; border: 4px solid #38bdf8; border-radius: 50%;
                            display: flex; flex-direction: column; justify-content: center; align-items: center;
                            box-shadow: 0 0 25px #38bdf8, 0 0 50px rgba(56, 189, 248, 0.5), inset 0 0 15px #38bdf8; background: #000000; padding: 10px; text-align: center;
                        }
                        .brand-text { font-size: 13px; font-weight: bold; color: #ffffff; font-family: sans-serif; text-shadow: 0 0 4px #38bdf8, 0 0 8px #38bdf8, 0 0 15px #38bdf8; }
                        .splash-loading-text { color: #ffffff; font-size: 14px; font-weight: 600; margin-top: 15px; font-family: sans-serif; text-shadow: 0 0 8px #38bdf8; }
                        .loading-dots { display: flex; gap: 6px; margin-top: 12px; }
                        .loading-dots span { width: 8px; height: 8px; background-color: #38bdf8; border-radius: 50%; box-shadow: 0 0 8px #38bdf8; animation: bounceDots 1.2s infinite ease-in-out; }
                        .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
                        .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
                        @keyframes bounceDots { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-8px); } }
                    </style>
                </head>
                <body>
                    <div class="neon-circle">
                        <span class="brand-text">Vida Official</span>
                    </div>
                    <div class="splash-loading-text">Načítava sa...</div>
                    <div class="loading-dots"><span></span><span></span><span></span></div>
                    <script>
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 10000);
                    </script>
                </body>
                </html>
                '''
            else:
                error_msg = "❌ Nesprávne heslo!"
        else:
            for u, info in data['users'].items():
                if info.get('email') == username:
                    user_exists = True
                    if info['password'] == password:
                        session['user'] = u
                        return '''
                        <!DOCTYPE html>
                        <html lang="sk">
                        <head>
                            <meta charset="UTF-8">
                            <title>Prihlasovanie...</title>
                            <style>
                                body { background: #000000; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; }
                                .neon-circle {
                                    width: 120px; height: 120px; border: 4px solid #38bdf8; border-radius: 50%;
                                    display: flex; flex-direction: column; justify-content: center; align-items: center;
                                    box-shadow: 0 0 25px #38bdf8, 0 0 50px rgba(56, 189, 248, 0.5), inset 0 0 15px #38bdf8; background: #000000; padding: 10px; text-align: center;
                                }
                                .brand-text { font-size: 13px; font-weight: bold; color: #ffffff; font-family: sans-serif; text-shadow: 0 0 4px #38bdf8, 0 0 8px #38bdf8, 0 0 15px #38bdf8; }
                                .splash-loading-text { color: #ffffff; font-size: 14px; font-weight: 600; margin-top: 15px; font-family: sans-serif; text-shadow: 0 0 8px #38bdf8; }
                                .loading-dots { display: flex; gap: 6px; margin-top: 12px; }
                                .loading-dots span { width: 8px; height: 8px; background-color: #38bdf8; border-radius: 50%; box-shadow: 0 0 8px #38bdf8; animation: bounceDots 1.2s infinite ease-in-out; }
                                .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
                                .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
                                @keyframes bounceDots { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-8px); } }
                            </style>
                        </head>
                        <body>
                            <div class="neon-circle">
                                <span class="brand-text">Vida Official</span>
                            </div>
                            <div class="splash-loading-text">Načítava sa...</div>
                            <div class="loading-dots"><span></span><span></span><span></span></div>
                            <script>
                                setTimeout(() => {
                                    window.location.href = '/';
                                }, 10000);
                            </script>
                        </body>
                        </html>
                        '''
                    else:
                        error_msg = "❌ Nesprávne heslo!"
                        break
            if not user_exists:
                error_msg = "❌ Účet neexistuje!"

    return f'''
    <!DOCTYPE html>
    <html lang="sk">
    <head><meta charset="UTF-8"><title>Prihlásenie</title></head>
    <body style="font-family:sans-serif; background:#fff; padding:40px; text-align:center;">
        <h2>Prihlásenie</h2>
        {f'<p style="background:#fee2e2; border:1px solid #fca5a5; color:#dc2626; padding:10px; border-radius:6px; max-width:300px; margin:0 auto 15px auto; font-size:13px; font-weight:bold;">{error_msg}</p>' if error_msg else ''}
        <form method="post" style="max-width:300px; margin:auto;">
        <input type="text" name="username" placeholder="Meno alebo Email" required style="width:100%; padding:10px; margin-bottom:10px;"><br>
        <input type="password" name="password" placeholder="Heslo" required style="width:100%; padding:10px; margin-bottom:10px;"><br>
        <button type="submit" style="background:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; width:100%;">Prihlásiť</button>
        </form>
        <br><p><a href="/forgot-password" style="color:#2563eb; text-decoration:none; font-weight:bold;">Zabudli ste prístup?</a></p>
        <br><a href="/">Domov</a>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(host='0.0.0.0', port=5000, debug=True)