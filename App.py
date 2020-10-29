from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt
app = Flask(__name__)

# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskcontacts'
mysql = MySQL(app)

# Settings
app.secret_key = 'mysecretkey'

#Semilla de encriptamiento
semilla = bcrypt.gensalt()


@app.route('/')
def main():
    if 'name' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/Index')
def Index():
    if 'name' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        return render_template('index.html', contacts = data)
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if (request.method=="GET"):
        if 'name' in session:
            return render_template('index.html')
        else:
            return render_template('login.html')
    else:
        name = request.form['NameSignup']
        email = request.form['EmailSignup']
        password = request.form['PasswordSignup']
        password_encode = password.encode("utf-8")
        password_encriptado = bcrypt.hashpw(password_encode, semilla)

        #Query para insercion
        sQuery = "INSERT into user(email, password, name) VALUES (%s, %s, %s)"
        cur = mysql.connection.cursor()
        cur.execute(sQuery, (email, password_encriptado, name))
        mysql.connection.commit()

        #Registrar la sesion
        session['name'] = name
        #session['email'] = email

        return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method=="GET"):
        if 'name' in session:
            return render_template('index.html')
        else:
            return render_template('login.html')
    else:
        email = request.form['EmailLogin']
        password = request.form['PasswordLogin']
        password_encode = password.encode("utf-8")
        cur = mysql.connection.cursor()

        #Query para consulta
        sQuery = "SELECT email, password, name, idUser FROM user WHERE email = %s"

        cur.execute(sQuery, [email])
        user = cur.fetchone()
        cur.close()

        #Verificar si obtuvo los datos
        if (user !=None):
            password_encriptado_encode = user[1].encode()

            if (bcrypt.checkpw(password_encode, password_encriptado_encode)):
                session['name'] = user[2]
                session['idUser'] = user[3]

                return redirect(url_for('Index'))
            else:
                #Password incorrecto
                flash("Acceso denegado", "alert-warning")
                return render_template('login.html')
        else:
            #print("El usuario no existe")
            flash("Acceso denegado", "alert-warning")
            return render_template('login.html')


@app.route("/salir")
def salir():
    # limpia la sesion
    session.clear()
    return redirect(url_for('login'))


@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts (fullname, phone, email) VALUES (%s, %s, %s)',
                    (fullname, phone, email))
        mysql.connection.commit()
        flash('Contact Added Successfully')
        return redirect(url_for('Index'))


@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE idContacts = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contact = data[0])


@app.route('/update/<id>', methods = ['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE contacts
        SET fullname = %s,
            email = %s,
            phone = %s
        WHERE  idContacts = %s
        """, (fullname,email,phone,id))
        mysql.connection.commit()
        flash('Contact Update Successfully')
        return redirect(url_for('Index'))


@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE idContacts = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('Index'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)