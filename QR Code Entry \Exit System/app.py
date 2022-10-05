from flask import (Flask, render_template, request,session,flash)
from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha
import qrcode
import MySQLdb

db = MySQLdb.connect("localhost", "root", "Thenu@12", "qrcode")
app = Flask(__name__)
app.secret_key='thenu'
app.config['CAPTCHA_ENABLE'] = True
app.config['CAPTCHA_LENGTH'] = 5
app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 50
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['CAPTCHA_SESSION_KEY'] = 'captcha_image'
app.config['SESSION_TYPE'] = 'sqlalchemy'
Session(app)
captcha = FlaskSessionCaptcha(app)

  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        code = request.form.get('code')
        password = request.form.get('password')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM admin WHERE code = % s AND password = % s', (code, password,))
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session['id'] = account[0]
            session['code'] = account[1]
            if captcha.validate():
                return render_template("register.html")
            else:
                flash('Wrong captcha', 'error')
                return render_template("login.html")
            
        flash('Wrong username or password', 'error')
        return render_template("login.html")

    return render_template("login.html")


@app.route('/register', methods =['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        sname = request.form.get('sname')
        regno = request.form.get('regno')
        department = request.form.get('department')
        stay = request.form.get('stay')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM students WHERE regno= % s', (regno, ))
        account = cursor.fetchone()
        if account:
            flash('Student already registered', 'error')
            return render_template("register.html")
        else:
            cursor.execute('INSERT INTO students VALUES (% s, % s, % s, % s)', (sname, regno, department,stay, ))
            db.commit()
            cursor.execute('SELECT * FROM students WHERE sname = % s AND regno= % s ', (sname,regno, ))
            stu = cursor.fetchone()
            sname = stu[0]
            regno = stu[1]
            department = stu[2]
            stay = stu[3]
            data=[]
            data.append(sname)
            data.append(regno)
            data.append(department)
            data.append(stay)
            qr = qrcode.QRCode(version = 1,
                   box_size = 10,
                   border = 5)
            qr.add_data(data)
            qr.make(fit = True)
            img = qr.make_image(fill_color = 'red',
                    back_color = 'white')
            img.save(regno +'.png')
            flash('Student registered successfully', 'success')
            return render_template("register.html")

if __name__ == "__main__":
     app.run(debug=True)