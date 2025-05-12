# import module flask ke dalam project
from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from MySQLdb.cursors import DictCursor

# membuat variabel sebagai instance flask
app = Flask(__name__)
# koneksi
app.secret_key = 'mauwisuda'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediksi_rating'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Ini yang benar
mysql = MySQL(app)

# membuat routing
@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM jenis_produk')
    jenis = cursor.fetchall()
    
    show_all_brand = request.args.get('show_all_brand') == 'true'
    show_all_produk = request.args.get('show_all_produk') == 'true'

    # Ambil brand
    cursor = mysql.connection.cursor()
    if show_all_brand:
        cursor.execute("SELECT * FROM brand")
    else:
        cursor.execute("SELECT * FROM brand LIMIT 3")
    brand = cursor.fetchall()

    # Ambil produk
    cursor = mysql.connection.cursor()
    if show_all_produk:
        cursor.execute("SELECT p.*, b.nama_brand, COALESCE(COUNT(u.id_ulasan), 0) AS jumlah_ulasan FROM produk p LEFT JOIN brand b ON p.id_brand = b.id_brand RIGHT JOIN ulasan u ON u.id_produk = p.id_produk GROUP BY p.id_produk, b.nama_brand")
    else:
        cursor.execute("SELECT p.*, b.nama_brand, COALESCE(COUNT(u.id_ulasan), 0) AS jumlah_ulasan FROM produk p LEFT JOIN brand b ON p.id_brand = b.id_brand LEFT JOIN ulasan u ON u.id_produk = p.id_produk GROUP BY p.id_produk, b.nama_brand LIMIT 8")
    produk = cursor.fetchall()
    
    cursor.close()

    return render_template('index.html', current_path=request.path, jenis=jenis, brand=brand, produk=produk)

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
        cursor.close()

        if akun is None:
            flash('Login Gagal, Cek Email Anda', 'danger')
        elif not check_password_hash(akun['password'], password):
            flash('Login Gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = akun['username']
            session['id_customer'] = akun['id_customer']
            return redirect(url_for('index'))
    return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Produk
@app.route('/produk')
def produk():
    if 'loggedin' not in session:
        flash('Harap Login Dulu', 'danger')
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()

    if search_query:
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id_produk) as total FROM produk p
            LEFT JOIN brand b ON p.id_brand = b.id_brand
            LEFT JOIN ulasan u ON u.id_produk = p.id_produk
            WHERE p.nama_produk LIKE %s
        """, ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT COUNT(*) as total FROM produk")

    total_produk = cursor.fetchone()['total']

    if search_query:
        cursor.execute('''
            SELECT p.*, b.nama_brand, COALESCE(COUNT(u.id_ulasan), 0) AS jumlah_ulasan
            FROM produk p
            LEFT JOIN brand b ON p.id_brand = b.id_brand
            LEFT JOIN ulasan u ON u.id_produk = p.id_produk
            WHERE p.nama_produk LIKE %s
            GROUP BY p.id_produk, b.nama_brand
            LIMIT %s OFFSET %s
        ''', ('%' + search_query + '%', per_page, offset))
    else:
        cursor.execute('''
            SELECT p.*, b.nama_brand, COALESCE(COUNT(u.id_ulasan), 0) AS jumlah_ulasan
            FROM produk p
            LEFT JOIN brand b ON p.id_brand = b.id_brand
            LEFT JOIN ulasan u ON u.id_produk = p.id_produk
            GROUP BY p.id_produk, b.nama_brand
            LIMIT %s OFFSET %s
        ''', (per_page, offset))

    produk = cursor.fetchall()
    cursor.close()

    total_pages = (total_produk + per_page - 1) // per_page

    return render_template('produk.html', show_search=True, produk=produk, page=page, total_pages=total_pages, search=search_query, current_path=request.path)

# tentang kami
@app.route('/tentang_kami')
def tentang_kami():
    return render_template('tentang_kami.html', current_path=request.path)
    
# Profile (GET untuk tampilkan, POST untuk update)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' not in session or 'id_customer' not in session:
        flash('Harap Login Dulu', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'personal_info':
            nama_lengkap = request.form.get('nama_lengkap')
            email = request.form.get('email')
            gender = request.form.get('jenis_kelamin')
            tgl_lahir = request.form.get('tgl_lahir')

            cursor.execute("""
                UPDATE customer 
                SET nama_lengkap=%s, email=%s, gender=%s, tgl_lahir=%s 
                WHERE id_customer = %s
            """, (nama_lengkap, email, gender, tgl_lahir, session['id_customer']))
            mysql.connection.commit()
            flash('Data personal berhasil diperbarui.', 'success')

        elif form_type == 'account_info':
            # Update username tanpa password
            username = request.form.get('username')
            
            # Ambil data customer dulu (untuk cek username lama)
            cursor.execute("SELECT username, password FROM customer WHERE id_customer = %s", (session['id_customer'],))
            account_data = cursor.fetchone()

            if not account_data:
                flash('Akun tidak ditemukan.', 'danger')
                return redirect(url_for('profile'))

            # Update username jika berbeda
            if username and username != account_data['username']:
                cursor.execute("""
                    UPDATE customer 
                    SET username=%s 
                    WHERE id_customer = %s
                """, (username, session['id_customer']))
                mysql.connection.commit()
                flash('Username berhasil diperbarui.', 'success')

            # Update password
            if request.form.get('password'):
                old_password = request.form.get('old_password')
                new_password = request.form.get('password')

                # Ambil password dari database untuk verifikasi
                cursor.execute("SELECT password FROM customer WHERE id_customer = %s", (session['id_customer'],))
                db_password = cursor.fetchone()

                if db_password is None:
                    flash('Akun tidak ditemukan.', 'danger')
                    return redirect(url_for('profile'))

                # Verifikasi password lama
                if not check_password_hash(db_password['password'], old_password):
                    flash('Password lama salah.', 'danger')
                    return redirect(url_for('profile'))

                # Verifikasi panjang password baru
                if len(new_password) < 6:
                    flash('Password minimal 6 karakter.', 'danger')
                    return redirect(url_for('profile'))

                # Hash password baru dan simpan
                hashed_password = generate_password_hash(new_password)
                cursor.execute("""
                    UPDATE customer 
                    SET password=%s 
                    WHERE id_customer = %s
                """, (hashed_password, session['id_customer']))
                mysql.connection.commit()
                flash('Password berhasil diperbarui.', 'success')
        
        return redirect(url_for('profile'))

    # Jika GET
    cursor.execute('SELECT * FROM customer WHERE id_customer = %s', (session['id_customer'],))
    account = cursor.fetchone()
    cursor.close()
    return render_template('profile.html', account=account)

@app.route('/produk/detail_produk/<string:id_produk>')
def detail_produk(id_produk):
    if 'loggedin' not in session or 'id_customer' not in session:
        flash('Harap Login Dulu', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    # Query dengan parameter (pastikan koma di tuple)
    cursor.execute('SELECT * FROM produk WHERE id_produk = %s', (id_produk,))
    cursor.execute('''
        SELECT p.*, b.nama_brand, COALESCE(COUNT(u.id_ulasan), 0) AS jumlah_ulasan
        FROM produk p
        LEFT JOIN brand b ON p.id_brand = b.id_brand
        LEFT JOIN ulasan u ON u.id_produk = p.id_produk
        WHERE p.id_produk = %s
        GROUP BY p.id_produk, b.nama_brand
    ''', (id_produk,))
    produk = cursor.fetchone()
    cursor.close()

    if produk is None:
        flash('Produk tidak ditemukan.', 'warning')
        return redirect(url_for('produk'))  # Atau redirect ke halaman produk

    return render_template('detail_produk.html', produk=produk)

@app.route('/produk/detail_produk/beri_ulasan')
def beri_ulasan():
    return render_template('detail_produk.html')
    
if __name__ == '__main__':
    app.run(debug=True)
    