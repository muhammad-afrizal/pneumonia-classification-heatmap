import os
import sys
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from db import create_connection, init_db, insert_history, get_all_history, register_user, authenticate_user, get_user_by_id, insert_feedback, get_feedback_by_history_id, get_all_feedback, get_feedback_stats, get_all_users, update_user_role
from env import DB_CONFIG, SECRET_KEY
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = SECRET_KEY

# Inisialisasi database
init_db()

# Load model
model = tf.keras.models.load_model("modelPneumonia.h5")
labels = ["Normal", "Pneumonia"]

def login_required(f):
    """Decorator untuk memeriksa apakah pengguna sudah login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator untuk memeriksa apakah pengguna adalah admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = get_user_by_id(session['user_id'])
        if not user or user[2] != 'admin':  # user[2] is role
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def non_admin_required(f):
    """Decorator untuk mencegah admin mengakses route tertentu"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = get_user_by_id(session['user_id'])
        if user and user[2] == 'admin':  # Jika pengguna adalah admin
            return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)

# Beranda / Landing Page
@app.route('/')
def index():
    user = getattr(g, 'user', None)
    records = get_all_history()
    return render_template('index.html', history=records, user=user)



# Form upload dan hasil prediksi
@app.route('/predict', methods=['GET', 'POST'])
@login_required
@non_admin_required
def predict():
    user = getattr(g, 'user', None)
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Load dan praproses gambar
            img = Image.open(filepath).convert('L').resize((150,150))
            img_array = np.array(img)
            
            # Terapkan CLAHE untuk meningkatkan kontras
            clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(8,8))
            img_clahe = clahe.apply(img_array)
            
            # Normalisasi kembali ke range [0,1]
            img_clahe_normalized = img_clahe / 255.0
            img_input = img_clahe_normalized.reshape(1, 150, 150, 1)  # Siapkan untuk input model

            # Lakukan prediksi tunggal tanpa TTA
            pred = model.predict(img_input)[0][0]
            prediction = labels[int(pred >= 0.5)]
            confidence = f"{(pred if pred >= 0.5 else 1 - pred)*100:.2f}%"

            # Simpan gambar CLAHE untuk ditampilkan dengan ukuran konsisten
            clahe_filename = f"clahe_{filename}"
            clahe_path = os.path.join('static/uploads', clahe_filename)
            clahe_pil_img = Image.fromarray(img_clahe)
            if clahe_pil_img.size != (150, 150):
                clahe_pil_img = clahe_pil_img.resize((150, 150), Image.LANCZOS)
            clahe_pil_img.save(clahe_path)
            
            # Saliency Map (gunakan gambar CLAHE untuk visualisasi)
            input_tensor = tf.convert_to_tensor(img_input)
            with tf.GradientTape() as tape:
                tape.watch(input_tensor)
                preds = model(input_tensor)
                top_class = tf.argmax(preds[0])
                top_output = preds[:, top_class]

            grads = tape.gradient(top_output, input_tensor)[0]
            saliency = np.abs(grads.numpy())
            saliency = np.max(saliency, axis=-1)
            saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min())

            # Save Saliency Map (berdasarkan CLAHE) dengan ukuran konsisten
            saliency_filename = f'saliency_{filename}'
            saliency_path = os.path.join('static/uploads', saliency_filename)
            plt.imsave(saliency_path, saliency, cmap='hot')
            
            # Pastikan ukuran saliency map konsisten
            saliency_img = Image.open(saliency_path)
            if saliency_img.size != (150, 150):
                saliency_img = saliency_img.resize((150, 150), Image.LANCZOS)
                saliency_img.save(saliency_path)

            # OVERLAY SALIENCY MAP (menggunakan gambar CLAHE)
            fig, ax = plt.subplots(figsize=(150/100, 150/100), dpi=100)  # Ukuran konsisten 150x150 pixels
            ax.imshow(img_clahe, cmap='gray')   # Gambar CLAHE grayscale (0-255)
            ax.imshow(saliency, cmap='hot', alpha=0.7)   # Overlay saliency map dengan transparansi
            ax.axis('off')
            ax.margins(0,0)
            ax.xaxis.set_major_locator(plt.NullLocator())
            ax.yaxis.set_major_locator(plt.NullLocator())

            # SAVE OVERLAY SALIENCY MAP dengan ukuran konsisten
            overlay_filename = f'overlay_{filename}'
            overlay_path = os.path.join('static/uploads', overlay_filename)
            plt.savefig(overlay_path, bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close()
            
            # Pastikan ukuran file overlay konsisten dengan gambar lain
            overlay_img = Image.open(overlay_path)
            if overlay_img.size != (150, 150):
                overlay_img = overlay_img.resize((150, 150), Image.LANCZOS)
                overlay_img.save(overlay_path)

            # Simpan ke database
            history_id = insert_history(session['user_id'], filename, prediction, confidence, clahe_filename, saliency_filename, overlay_filename)

            return render_template('result.html',
                                   filename=filename,
                                   clahe_filename=clahe_filename,
                                   saliency_filename=saliency_filename,
                                   overlay_filename=overlay_filename,
                                   prediction=prediction,
                                   confidence=confidence,
                                   saliency=saliency.tolist(),
                                   history_id=history_id,
                                   user=user)
    return render_template('predict.html', user=user)

# Riwayat prediksi
@app.route('/history')
@login_required
@non_admin_required
def history():
    user = getattr(g, 'user', None)
    print(f"DEBUG: User accessing history - ID: {session.get('user_id')}, Username: {user[1] if user else 'None'}")
    history_records = get_all_history(session['user_id'])
    print(f"DEBUG: Found {len(history_records)} history records for user {session.get('user_id')}")
    return render_template('history.html', history=history_records, user=user)

# Submit feedback
@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    user = getattr(g, 'user', None)
    if request.method == 'POST':
        history_id = request.form.get('history_id')
        is_accurate = request.form.get('is_accurate')
        usefulness_rating = request.form.get('usefulness_rating')
        reason = request.form.get('reason', '')
        
        # Convert values
        is_accurate = is_accurate == 'true'
        usefulness_rating = int(usefulness_rating) if usefulness_rating else None
        
        # Insert feedback
        insert_feedback(history_id, is_accurate, usefulness_rating, reason)
        
        return jsonify({'status': 'success'})

# Halaman registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if register_user(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Registration failed")
    
    return render_template('register.html')

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_id = authenticate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            # Check if user is admin
            user = get_user_by_id(user_id)
            if user and user[2] == 'admin':  # user[2] is role
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    user = getattr(g, 'user', None)
    # Get statistics
    stats = get_feedback_stats()
    # Get all history
    all_history = get_all_history()
    # Get all feedback
    all_feedback = get_all_feedback()
    # Get all users
    all_users = get_all_users()
    
    return render_template('admin/dashboard.html', 
                          user=user, 
                          stats=stats, 
                          history=all_history,
                          feedback=all_feedback,
                          users=all_users)

# Admin user management
@app.route('/admin/users/<int:user_id>/role', methods=['POST'])
@admin_required
def update_user_role_route(user_id):
    role = request.form.get('role', 'user')
    update_user_role(user_id, role)
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
