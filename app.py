from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cv2
import numpy as np
import os
import base64
import json
from datetime import datetime

from face_detector import detect_face_violations
from violation_logger import log_violation
from report_generator import generate_report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_proctoring_super_secret_key_2026_very_long_and_secure'  # ← Changed to config
app.config['SESSION_COOKIE_SECURE'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================== USER CLASS ==================
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# ================== USER MANAGEMENT ==================
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'student': {'password': 'password', 'role': 'student'},
        'admin': {'password': 'adminpass', 'role': 'admin'}
    }

def save_users(users_dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_dict, f, indent=4)

users = load_users()

# ================== ROUTES ==================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if users.get(current_user.id, {}).get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('exam'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username in users:
            return render_template('register.html', error="Username already exists!")
        if len(username) < 3 or len(password) < 4:
            return render_template('register.html', error="Username min 3 chars, Password min 4 chars.")
        
        users[username] = {'password': password, 'role': 'student'}
        save_users(users)
        
        print(f"✅ New user registered: {username}")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if users.get(current_user.id, {}).get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('exam'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"🔍 Login attempt - Username: '{username}' | Password: '{password}'")
        
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user, remember=True)
            print(f"✅ SUCCESS: User '{username}' logged in successfully!")
            
            if users[username]['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('exam'))
        else:
            print("❌ Invalid credentials")
            return render_template('login.html', error="Invalid username or password. Try 'student' / 'password'")
    
    return render_template('login.html')

@app.route('/exam')
@login_required
def exam():
    return render_template('exam.html')

@app.route('/analyze_frame', methods=['POST'])
@login_required
def analyze_frame():
    data = request.json
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    violations = detect_face_violations(frame)
    
    for violation in violations:
        log_violation(current_user.id, violation, datetime.now())
    
    return jsonify({'violations': violations})

@app.route('/finish_exam', methods=['POST'])
@login_required
def finish_exam():
    report_path = generate_report(current_user.id)
    return jsonify({'report': report_path})

@app.route('/admin')
@login_required
def admin_dashboard():
    if users.get(current_user.id, {}).get('role') != 'admin':
        return redirect(url_for('exam'))
    reports = [f for f in os.listdir('reports') if f.endswith('.html')]
    return render_template('admin.html', reports=reports)

@app.route('/reports/<filename>')
@login_required
def serve_report(filename):
    return send_from_directory('reports', filename)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)