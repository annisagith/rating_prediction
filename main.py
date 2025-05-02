# import module flask ke dalam project
from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash

# membuat variabel sebagai instance flask
app = Flask(__name__)
# koneksi
app.secret_key = 'mauwisuda'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediksi_rating'
mysql = MySQL(app)

# membuat routing
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html')
    flash('Harap Login Dulu', 'danger')
    return redirect(url_for('login'))

# registrasi
@app.route('/registrasi/', methods=('GET', 'POST'))
def registrasi():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        nama_lengkap = request.form['nama_lengkap']
        # Validasi password minimal 6 karakter
        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'danger')
            return render_template('registrasi.html')

        # cek username atau email
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM customer WHERE username=%s OR email=%s', (username, email, ))
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('''INSERT INTO customer (id_customer, username, password, email, nama_lengkap, created_at, updated_at) VALUES (UUID(), %s, %s, %s, %s, NOW(), NOW())''', (username, generate_password_hash(password), email, nama_lengkap))
            mysql.connection.commit()
            flash('Registration Berhasil Silakan login.', 'success')
            # return redirect(url_for('login'))  # redirect setelah berhasil
        else:
            flash('Username atau email sudah terdaftar.', 'danger')
    return render_template('registrasi.html')

@app.route('/login/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # cek data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM customer WHERE email=%s', (email, ))
        akun = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek Email Anda', 'danger')
        elif not check_password_hash(akun[2], password):
            flash('Login Gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = akun[1]
            return redirect(url_for('index'))
    return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return '<h1>About Us</h1>'

@app.route('/contact')
def contact():
    return '<h1>Contact Us</h1>'

@app.route('/profile')
def profile():
    return '<h1>Profile</h1>'

@app.route('/profile/<username>')
def profile_name(username):
    return '<h1>Hello %s!</h1>' % username

if __name__ == '__main__':
    app.run(debug=True)
    