import datetime
import os
import pymysql.cursors
from flask import Flask, jsonify, redirect, render_template, request, url_for, session

application = Flask(__name__)
application.secret_key = 'your_secret_key'

conn = cursor = None

def openDb():
    global conn, cursor
    conn = pymysql.connect(db="sea-salon", user="root", passwd="",host="localhost",port=3306,autocommit=True)
    cursor = conn.cursor()	

def closeDb():
    global conn, cursor
    cursor.close()
    conn.close()

def generate_nik():
    openDb()
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    year_str = str(current_year).zfill(2)
    current_month_str = str(current_month).zfill(2)
    base_nik_without_number = f"{year_str}{current_month_str}"
    cursor.execute("SELECT id FROM login WHERE id LIKE %s ORDER BY id DESC LIMIT 1", (f"{base_nik_without_number}%",))
    last_nik = cursor.fetchone()
    if last_nik:
        last_number = int(last_nik[0].split("-")[-1])
        next_number = last_number + 1
        next_nik = f"P-{str(next_number).zfill(3)}"
    else:
        next_number = 1
        next_nik = f"{base_nik_without_number}{str(next_number).zfill(3)}"
    closeDb()
    return next_nik

@application.route('/index')
def index():
    openDb()
    container2 = []
    sql = "SELECT * FROM cabang;"
    cursor.execute(sql)
    results2 = cursor.fetchall()
    for data in results2:
        container2.append(data)
    closeDb()
    return render_template('index.html', container2=container2)

@application.route('/admin')
def admin():
    openDb()
    container = []
    container2 = []
    sql = "SELECT * FROM reservasi;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for data in results:
        container.append(data)
    sql = "SELECT * FROM cabang;"
    cursor.execute(sql)
    results2 = cursor.fetchall()
    for data in results2:
        container2.append(data)
    closeDb()
    return render_template('admin/index.html', container=container, container2=container2)

@application.route('/regist', methods=['GET', 'POST'])
def regist():
    generated_nik = generate_nik()
    if request.method == 'POST':
        nik = request.form['nik']
        nama = request.form['nama']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']
        openDb()
        sql = "INSERT INTO login (id, nama, email, phone, password, role) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (nik, nama, email, phone, password, role)
        cursor.execute(sql, val)
        sql = "UPDATE login SET password=SHA(%s) WHERE id=%s"
        val = (password, nik)
        cursor.execute(sql, val)
        conn.commit()
        closeDb()
        return redirect('/')
    else:
        return render_template('register.html', nik=generated_nik)

@application.route('/', methods=['GET', 'POST'])
def login():
    openDb()
    try:
        if request.method == 'POST':
            nama = request.form['nama']
            password = request.form['password']
            cursor.execute('SELECT * FROM login WHERE nama=%s', (nama,))
            data = cursor.fetchone()
            val = (nama, password)
            cursor.execute('SELECT COUNT(*) FROM login WHERE nama=%s AND password=SHA(%s);', val)
            data2 = cursor.fetchone()
            if data[5] == 'user':
                if data2[0] <= 0:
                    closeDb()
                    return redirect('/')
                else:
                    closeDb()
                    session['user'] = nama
                    return redirect(url_for('index'))
            else:
                if data2[0] <= 0:
                    closeDb()
                    return redirect('/')
                else:
                    closeDb()
                    session['user'] = nama
                    return redirect(url_for('admin'))
    except:
        print('error')
    closeDb()
    return render_template("login.html")

@application.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@application.route('/submit_review', methods=['POST'])
def submit_review():
    if request.method == 'POST':
        nama = request.form['nama']
        rating = request.form['rate']
        komen = request.form['comment']
        openDb()
        sql = "INSERT INTO review (nama, rating, komen) VALUES (%s, %s, %s)"
        val = (nama, rating, komen)
        cursor.execute(sql, val)
        conn.commit()
        closeDb()
        return redirect('/index')

@application.route('/proses_pesan', methods=['POST'])
def proses_pesan():
    
    if request.method == 'POST':
        nama = request.form['nama']
        date = request.form['cek_in']
        waktu = request.form['time']
        servis = request.form['servis']
        hp = request.form['hp']
        cabang = request.form['branch']
        print(cabang)
       
        openDb()
        sql = "INSERT INTO reservasi (nama,handphone,servis,tanggal,waktu,cabang) VALUES (%s, %s, %s, %s, %s,%s)"
        val = (nama,hp,servis,date,waktu, cabang)
        cursor.execute(sql, val)
        conn.commit()
        closeDb()
        return redirect('/index')

@application.route('/branch', methods=['POST'])
def branch():
    if request.method == 'POST':
        nama = request.form['name']
        lokasi = request.form['location']
        buka = request.form['open']
        tutup = request.form['close']
        openDb()
        sql = "INSERT INTO cabang (nama, lokasi, buka, tutup) VALUES (%s, %s, %s, %s)"
        val = (nama, lokasi, buka, tutup)
        cursor.execute(sql, val)
        conn.commit()
        closeDb()
        return redirect('/admin')

@application.route('/edit', methods=['POST'])
def edit():
        
        if request.method == 'POST':
            select = request.form['select']
            nama = request.form['name']
            lokasi = request.form['location']
            buka = request.form['open']
            tutup = request.form['close']

            openDb()
            sql = "UPDATE cabang SET nama=%s, lokasi=%s, buka=%s, tutup=%s WHERE nama=%s"
            val = (nama, lokasi, buka, tutup, select)
            cursor.execute(sql, val)
            conn.commit()
            closeDb()
            return redirect(url_for('admin'))

if __name__ == '__main__':
    application.run(debug=True)
