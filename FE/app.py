from flask import Flask, render_template, request, session, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'lettusense_fe'

BACKEND_URL = 'https://belettusense-production.up.railway.app'


@app.route('/')
def index():
     return render_template('FE/templates/landing.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        payload = {
            'username': request.form['username'],
            'password': request.form['password']
        }
        response = requests.post(f'{BACKEND_URL}/register', json=payload)
        if response.ok:
            flash('Registrasi berhasil! Silakan login.')
            return redirect(url_for('login'))
        else:
            flash('Registrasi gagal. Username mungkin sudah digunakan.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        payload = {
            'username': request.form['username'],
            'password': request.form['password']
        }
        response = requests.post(f'{BACKEND_URL}/login', json=payload)
        if response.ok:
            data = response.json()
            session['user_id'] = data['user_id']
            session['username'] = payload['username']
            return redirect(url_for('home'))
        else:
            flash('Login gagal. Periksa username dan password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil.')
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    prediction = None
    image_url = None

    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            files = {'file': file}
            data = {'user_id': session['user_id']}
            response = requests.post(f'{BACKEND_URL}/predict', files=files, data=data)
            if response.ok:
                result = response.json()
                prediction = f"{result['prediction']} ({result['confidence']}%)"
                image_url = f"{BACKEND_URL}/uploads/{result['filename']}"
            else:
                flash('Gagal memproses gambar.')

    return render_template('home.html', prediction=prediction, image_url=image_url)

# === Filter GMT+7 untuk template ===
@app.template_filter('to_gmt7')
def to_gmt7_filter(value):
    try:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        dt += timedelta(hours=7)
        return dt.strftime('%d %b %Y %H:%M')
    except Exception:
        return value

# === Route riwayat ===
@app.route('/riwayat')
def riwayat():
    if 'user_id' not in session:
        flash('Silakan login untuk melihat riwayat.')
        return redirect(url_for('login'))

    response = requests.get(f'{BACKEND_URL}/riwayat/{session["user_id"]}')
    if response.ok:
        data = response.json()
        return render_template('riwayat.html', riwayat=data['riwayat'], backend_url=BACKEND_URL)
    else:
        flash('Gagal memuat riwayat.')
        return render_template('riwayat.html', riwayat=[], backend_url=BACKEND_URL)


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

