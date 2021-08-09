import os
import secrets
from PIL import Image
from flask import render_template, url_for, request, redirect, jsonify, flash, request
from app import app, db, bcrypt
from app.models import Usuario, Fonte, Quantidade, Bebida, Vendas
from app.forms import RegistrationForm, LoginForm, BebidaForm, PesoForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/app",  methods=['POST', 'GET'])
def root_app():
    if current_user.is_authenticated:
        if current_user.admin == 1:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('album'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('album'))
        else:
            flash('Usuário ou senha incorretos. Por favor, tente novamente.', 'danger')
    return render_template('sing-in.html', form=form)

@app.route("/app/registration",  methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        dic = {'username':form.username.data, 'password':hashed_pw, 'dinheiro':0}    
        if len(form.admin.data) == 0:
            dic.update({'admin':0})
            db.session.add(Usuario(**dic))
            db.session.commit()
            flash(f'Conta {form.username.data} criada com sucesso!', 'success')
            return redirect(url_for('album'))
        else:
            dic.update({'admin':1})
            db.session.add(Usuario(**dic))
            db.session.commit()
            flash(f'Conta {form.username.data} criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form)

@app.route("/app/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('root_app'))

@app.route("/app/dashboard")
@login_required
def dashboard():
    if current_user.admin == 0:
        return redirect(url_for('album'))
        
    return render_template('dashboard.html')

@app.route("/app/album")
@login_required
def album():
    return render_template('album.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static','images','fontes',picture_fn)
    output_size = (800,600)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/app/heroes", methods=['GET', 'POST'])
@login_required
def heroes():
    bebidaForm = BebidaForm()
    pesoForm= PesoForm()
    fonte1 = {'imagem':url_for('static', filename='images/fontes/default.jpg'),
            'nome': 'Sem fonte cadastrada',
            'quantidade': '0ml/0ml'}
    if request.method == 'POST':
        if bebidaForm.validate_on_submit():
            if bebidaForm.picture.data:
                picture_file = save_picture(bebidaForm.picture.data)
            return redirect(url_for('album'))
        elif bebidaForm.submitBebida.data:
            return render_template('heroes.html', bebidaClick=True, fonte1=fonte1, bebidaForm=bebidaForm, pesoForm=pesoForm)

        if pesoForm.validate_on_submit():
            return redirect(url_for('album'))
        elif pesoForm.submitPeso.data:
            return render_template('heroes.html', pesoClick=True, fonte1=fonte1, bebidaForm=bebidaForm, pesoForm=pesoForm)
        
    return render_template('heroes.html', fonte1=fonte1, bebidaForm=bebidaForm, pesoForm=pesoForm)

#Blog routes

@app.route("/", methods=['POST', 'GET'])
def hello_world():
    if request.method=='POST':
        if 'e2' in request.form:
            return redirect(url_for('e2'))
        elif 'e3' in request.form:
            return redirect(url_for('e3'))
        elif 'e4' in request.form:
            return redirect(url_for('e4'))
        elif 'e5' in request.form:
            return redirect(url_for('e5'))
    return render_template('project-detail.html')

@app.route("/e2", methods=['POST','GET'])
def e2():
    if request.method=='POST':
        return redirect(url_for('hello_world'))
    return render_template('e2.html')

@app.route("/e3", methods=['POST','GET'])
def e3():
    if request.method=='POST':
        return redirect(url_for('hello_world'))
    return render_template('e3.html')

@app.route("/e4", methods=['POST','GET'])
def e4():
    if request.method=='POST':
        return redirect(url_for('hello_world'))
    return render_template('e4.html')

@app.route("/e5", methods=['POST','GET'])
def e5():
    if request.method=='POST':
        return redirect(url_for('hello_world'))
    return render_template('e5.html')

# API routes
ip_global = "vazio"

@app.route("/api")
def get_ip():    
    global ip_global
    return {'ip':ip_global}

@app.route("/api/ip", methods=['POST'])
def set_ip():
    global ip_global
    data = request.json
    if "cookie" in data:
        if data['cookie'] == "Mugiwara":
            ip_global = data['ip']
            return {"ip":ip_global}
    return "Wrong data", 404
