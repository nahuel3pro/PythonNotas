from flask import Flask, render_template,url_for,request, flash,redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import login_manager, login_user, login_required, logout_user, current_user
import datetime as dt
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'etovsyo'

db = SQLAlchemy(app)
DB_NAME = 'database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///bds/{DB_NAME}'

#   Modelo de base de datos
class Agenda(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    texto = db.Column(db.String(10000))
    fecha = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(255), unique = True)
    user = db.Column(db.String(255))
    password = db.Column(db.String(255))
    notes = db.relationship('Agenda')

#   Creando la base de datos
db.create_all(app = app)

login_manager = login_manager.LoginManager()
login_manager.login_view = 'home'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

#   Direcciones

@app.route('/')
def home():
    return render_template('index.html', user=current_user)

@app.route('/PP', methods = ['POST', 'GET'])
@login_required
def pp():
    if request.method == 'POST':
        texto = request.form.get('texto_nota')
        date = request.form.get('date')

        fecha = dt.datetime.strptime(date, "%Y-%m-%d")
        fecha = fecha.date()
        
        print(fecha)
        print(type(fecha))

        nueva_nota = Agenda( texto = texto, fecha = fecha, user_id = current_user.id)
        db.session.add(nueva_nota)
        db.session.commit()

    else:
        return render_template('home.html', user = current_user)
    return render_template('home.html', user=current_user)

@app.route('/registrarse', methods = ['POST','GET'])
def registrarse():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')
        contraseña2 = request.form.get('contraseña2')

        mail = Usuario.query.filter_by(email = email).first()

        if mail:
            flash('¡Ya hay una cuenta con ese mail!' , category='error')
        elif contraseña != contraseña2:
            flash('Las contraseñas no coinciden', category='error')
        elif len(contraseña) < 7:
                flash('La contraseña debe ser mayor a 7 caractéres', category='error')
        else:
            new_user = Usuario(email = email, user = usuario, password = generate_password_hash(contraseña, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            # login_user(mail, remember=True)

            flash('¡Registrado!', category='tolis')

            return redirect(url_for('home'))
            

    return render_template('registrarse.html', user=current_user)

@app.route('/Ingresar', methods = ['POST', 'GET'])
def ingresar():
    if request.method == 'POST':
        email = request.form.get('email')
        contraseña = request.form.get('contraseña')

        mail = Usuario.query.filter_by(email = email).first()

        if mail:
            if check_password_hash(mail.password , contraseña):
                login_user(mail, remember=True)
                return redirect(url_for('pp'))
            else:
                flash('Contraseña Incorrecta', category='error')
        else:
            flash('Ese email no está registrado', category='error')
    
    
    return render_template('ingresar.html' , user=current_user)

@app.route('/cerrar')
@login_required
def cerrar():
    logout_user()
    return redirect(url_for('home'))

@app.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Agenda.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@app.route('/editar/<string:id>', methods=['POST', 'GET'])
def editar_note(id):
    
    
    if request.method == 'POST':
        text = Agenda.query.get(id)

        new_date = request.form.get('date')
        texto_nota = request.form.get('texto_nota')

        # Formateando la fecha para que la acepte
        fecha_nueva = dt.datetime.strptime(new_date, "%Y-%m-%d")
        fecha_nueva = fecha_nueva.date()

        print(fecha_nueva)
        print(type(fecha_nueva))
        

        # nueva_data = text(fecha = fecha_nueva, texto = texto_nota, user_id = current_user.id)
        # db.session.add(nueva_data)
        text.texto = texto_nota
        text.fecha = fecha_nueva
        db.session.commit()

        return redirect(url_for('pp'))
    else:
        texto = Agenda.query.filter_by(id = id).first()
        
        print(texto.texto)

        return render_template('editar.html', user=current_user, texto = texto)

if __name__ == "__main__":
    app.run(debug=True)