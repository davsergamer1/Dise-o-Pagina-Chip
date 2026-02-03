from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# -----------------------------------------
# 🔧 CONFIGURACIÓN GENERAL
# -----------------------------------------
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/refritati_db')
DB_NAME = os.getenv('DB_NAME', 'refritati_db')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_change_me')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db['users']
readings = db['readings']

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 📂 Configuración de subida de imágenes
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 📧 CONFIGURACIÓN DE CORREO
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'davsergamer@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'qpof stuy vvmy lgnl')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)


# -----------------------------------------
# 🔍 FUNCIONES AUXILIARES
# -----------------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return users.find_one({'_id': ObjectId(uid)})


# -----------------------------------------
# 🏠 RUTAS PRINCIPALES
# -----------------------------------------
@app.route('/')
def home():
    user = current_user()

    # 🟢 Traer los 3 comentarios más recientes
    recent_comments = list(db['comments'].find().sort('created_at', -1).limit(3))
    for c in recent_comments:
        c['_id'] = str(c['_id'])
        c['created_at'] = c['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    if user:
        return render_template('index.html', user=user, comments=recent_comments)

    return render_template('index.html', comments=recent_comments)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if users.find_one({'email': email}):
            flash('⚠️ Email ya registrado', 'error')
            return redirect(url_for('register'))

        pw_hash = generate_password_hash(password)

        # 🧠 Si el correo es el del admin supremo, se le asigna automáticamente el rol de admin
        role = 'admin' if email == 'davsergamer@gmail.com' else 'user'

        res = users.insert_one({
            'username': username,
            'email': email,
            'password': pw_hash,
            'role': role,
            'autoSave': False,
            'interval': 5,
            'created_at': datetime.utcnow(),
            'profile_pic': None
        })
        session['user_id'] = str(res.inserted_id)
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users.find_one({'email': email})

        if not user or not check_password_hash(user['password'], password):
            flash('❌ Credenciales inválidas', 'error')
            return redirect(url_for('login'))

        # Si el usuario admin principal inicia sesión, asegurar rol admin
        if user['email'] == 'davsergamer@gmail.com' and user.get('role') != 'admin':
            users.update_one({'_id': user['_id']}, {'$set': {'role': 'admin'}})
            user['role'] = 'admin'

        session['user_id'] = str(user['_id'])
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# -----------------------------------------
# 📊 DASHBOARD
# -----------------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    # === Envío de comentarios ===
    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '').strip()

        if rating < 1 or rating > 5:
            flash('Selecciona una calificación válida.', 'error')
            return redirect(url_for('dashboard'))

        if not comment:
            flash('Escribe un comentario antes de enviar.', 'error')
            return redirect(url_for('dashboard'))

        db['comments'].insert_one({
            'user_id': str(user['_id']),
            'username': user['username'],
            'rating': rating,
            'comment': comment,
            'created_at': datetime.utcnow()
        })
        flash('✅ Comentario enviado con éxito.', 'success')
        return redirect(url_for('dashboard'))

    # === Obtener comentarios recientes ===
    comments = list(
        db['comments'].find().sort('created_at', -1).limit(10)
    )

    # Convertir fechas a formato legible
    for c in comments:
        c['created_at'] = c['created_at'].strftime("%Y-%m-%d %H:%M")

    # Renderizar dashboard con feedback incluido
    return render_template(
        'dashboard.html',
        user=user,
        feedbacks=comments
    )


    # === Mostrar comentarios existentes ===
    all_comments = list(db['comments'].find().sort('created_at', -1))
    for c in all_comments:
        c['_id'] = str(c['_id'])
        c['is_owner'] = (c['user_id'] == str(user['_id']))
        c['is_admin'] = (user.get('role') == 'admin')
        c['created_at'] = c['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return render_template('dashboard.html', user=user, feedbacks=all_comments)



# -----------------------------------------
# 👤 PERFIL DE USUARIO
# -----------------------------------------
@app.route('/profile')
def profile():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    user = current_user()
    if not user:
        return jsonify({'error': 'unauthenticated'}), 401

    data = request.get_json()
    username = data.get('username', user['username'])
    email = data.get('email', user['email'])
    autoSave = data.get('autoSave') in [True, "true", "on"]
    interval = int(data.get('interval', 5))

    users.update_one(
        {'_id': user['_id']},
        {'$set': {
            'username': username,
            'email': email,
            'autoSave': autoSave,
            'interval': interval
        }}
    )

    return jsonify({'message': '✅ Perfil actualizado correctamente'})


# -----------------------------------------
# 🖼️ SUBIR FOTO DE PERFIL
# -----------------------------------------
@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    user = current_user()
    if not user:
        return jsonify({'error': 'unauthenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'no file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'empty filename'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{str(user['_id'])}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        rel_path = f"/static/uploads/{filename}"
        users.update_one({'_id': user['_id']}, {'$set': {'profile_pic': rel_path}})

        return jsonify({'message': '✅ Foto de perfil actualizada', 'path': rel_path})

    return jsonify({'error': '❌ Formato no permitido (solo jpg, png, gif)'}), 400


# -----------------------------------------
# 📈 API DE LECTURAS
# -----------------------------------------
@app.route('/api/readings', methods=['POST'])
def create_reading():
    data = request.get_json(force=True)
    device_id = data.get('device_id', 'unknown-device')

    try:
        cholesterol = float(data.get('cholesterol', 0))
        sugar = float(data.get('sugar', 0))
        fever = float(data.get('fever', 0))
    except Exception:
        return jsonify({'error': 'invalid numeric values'}), 400

    user_id = data.get('user_id')
    doc = {
        'device_id': device_id,
        'cholesterol': cholesterol,
        'sugar': sugar,
        'fever': fever,
        'user_id': user_id,
        'timestamp': datetime.utcnow()
    }

    alert = (
        cholesterol < 125 or cholesterol > 200 or
        sugar < 70 or sugar > 140 or
        fever < 36 or fever > 37.5
    )
    doc['alert'] = alert

    readings.insert_one(doc)
    return jsonify({'message': 'lectura guardada', 'alert': alert}), 201


@app.route('/api/latest_reading')
def latest_reading():
    user = current_user()
    if not user:
        return jsonify({'error': 'unauthenticated'}), 401

    last = readings.find_one({'user_id': str(user['_id'])}, sort=[('timestamp', -1)])
    if not last:
        return jsonify({'message': 'No readings yet'})

    last['_id'] = str(last['_id'])
    last['timestamp'] = last['timestamp'].isoformat()
    return jsonify(last)


# -----------------------------------------
# 👑 ADMINISTRACIÓN (solo admin supremo)
# -----------------------------------------
@app.route('/api/make_admin', methods=['POST'])
def make_admin():
    user = current_user()
    if not user or user['email'] != 'davsergamer@gmail.com':
        return jsonify({'error': 'unauthorized'}), 403

    data = request.get_json(force=True)
    email_to_promote = data.get('email')

    target = users.find_one({'email': email_to_promote})
    if not target:
        return jsonify({'error': 'usuario no encontrado'}), 404

    users.update_one({'_id': target['_id']}, {'$set': {'role': 'admin'}})
    return jsonify({'message': f'✅ {email_to_promote} ahora es administrador'})


@app.route('/api/users')
def list_users():
    user = current_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 403

    all_users = list(users.find({}, {'password': 0}))
    for u in all_users:
        u['_id'] = str(u['_id'])
    return jsonify(all_users)


# -----------------------------------------
# 🌐 PÁGINAS INFORMATIVAS
# -----------------------------------------
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/pqr', methods=['GET', 'POST'])
def pqr():
    """Formulario PQR que envía un correo al administrador."""
    if request.method == 'POST':
        nombre = request.form.get('name')
        correo = request.form.get('email')
        mensaje = request.form.get('message')

        try:
            msg = Message(
                subject=f"Nuevo PQR de {nombre}",
                recipients=['davsergamer@gmail.com'],
                body=f"📬 Nuevo mensaje desde Sensor Health\n\n"
                     f"👤 Nombre: {nombre}\n"
                     f"📧 Correo: {correo}\n\n"
                     f"💬 Mensaje:\n{mensaje}"
            )
            mail.send(msg)
            flash('✅ Tu mensaje fue enviado correctamente.', 'success')
        except Exception as e:
            print(f"Error enviando correo: {e}")
            flash('❌ Error al enviar el mensaje. Intenta más tarde.', 'error')

        return redirect(url_for('pqr'))

    return render_template('pqr.html')


# -----------------------------------------
# ⚠️ MANEJO DE ERRORES
# -----------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404



# -----------------------------------------
# 💬 COMENTARIOS Y CALIFICACIONES
# -----------------------------------------
comments = db['comments']


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    user = current_user()
    if not user:
        flash('Debes iniciar sesión para dejar un comentario.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '').strip()

        if rating < 1 or rating > 5:
            flash('Selecciona una calificación válida.', 'error')
            return redirect(url_for('feedback'))

        if not comment:
            flash('Escribe un comentario antes de enviar.', 'error')
            return redirect(url_for('feedback'))

        comments.insert_one({
            'user_id': str(user['_id']),
            'username': user['username'],
            'rating': rating,
            'comment': comment,
            'created_at': datetime.utcnow()
        })
        flash('✅ Comentario enviado con éxito.', 'success')
        return redirect(url_for('feedback'))

    # Mostrar comentarios existentes
    all_comments = list(comments.find().sort('created_at', -1))
    for c in all_comments:
        c['_id'] = str(c['_id'])
        c['is_owner'] = (c['user_id'] == str(user['_id']))
        c['is_admin'] = (user.get('role') == 'admin')
        c['created_at'] = c['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return render_template('feedback.html', user=user, comments=all_comments)


@app.route('/delete_comment/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'unauthenticated'}), 401

    comment = comments.find_one({'_id': ObjectId(comment_id)})
    if not comment:
        return jsonify({'error': 'comment not found'}), 404

    # Solo el admin o el autor puede eliminar
    if user.get('role') == 'admin' or comment['user_id'] == str(user['_id']):
        comments.delete_one({'_id': ObjectId(comment_id)})
        flash('🗑️ Comentario eliminado correctamente.', 'success')
        return redirect(url_for('feedback'))
    else:
        return jsonify({'error': 'unauthorized'}), 403
    




# -----------------------------------------
# 🚀 EJECUCIÓN
# -----------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
