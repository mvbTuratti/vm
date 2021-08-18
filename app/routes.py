import os
import csv
import secrets
from PIL import Image
from flask import render_template, url_for, request, redirect, jsonify, flash, request
from app import app, db, bcrypt
from app.models import Usuario, Fonte, Quantidade, Bebida, Vendas
from app.forms import RegistrationForm, LoginForm, BebidaForm, PesoForm, DinheiroForm, FontesAtivarForm, RemoverFonteForm
from flask_login import login_user, current_user, logout_user, login_required
from app.pesos import log_peso, get_last_peso
from app.bombas import bebida

@app.route("/app",  methods=['POST', 'GET'])
def root_app():
    if current_user.is_authenticated:
        if current_user.admin == 1:
            return redirect(url_for('heroes'))
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
            return redirect(url_for('heroes'))
    
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
    
    bebidas_validas = Bebida.query.all()
    for b in bebidas_validas:

        try:
            if Fonte.query.filter_by(id=Quantidade.query.filter_by(id=b.quantidade1).first().fonte).first().available == 0:
                b.available = 0
                break
        except:
            pass
        try:
            if Fonte.query.filter_by(id=Quantidade.query.filter_by(id=b.quantidade2).first().fonte).first().available == 0:
                b.available = 0
                break
        except:
            pass
        try:
            if Fonte.query.filter_by(id=Quantidade.query.filter_by(id=b.quantidade3).first().fonte).first().available == 0:
                b.available = 0
                break
        except:
            pass
    try:
        db.session.commit()
    except:
        db.session.rollback()


    bebidas = [{'imagem':url_for('static', filename=f'images/bebidas/{bebida.image_file}'),
                'nome':bebida.nome, 'total':bebida.total} for bebida in Bebida.query.all() if bebida.available > 0]
    return render_template('album.html', dinheiro=current_user.dinheiro, bebidas=bebidas)

def save_picture(form_picture, folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static','images',folder,picture_fn)
    output_size = (480,480)
    i= Image.open(form_picture)
    if i.mode != 'RGB':
        i.convert('RGB')
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/app/heroes", methods=['GET', 'POST'])
@login_required
def heroes():
    if current_user.admin == 0:
        return redirect(url_for('album'))
    bebidaForm = BebidaForm()
    pesoForm= PesoForm()
    dinheiroForm = DinheiroForm()
    fonteAtivaForm = FontesAtivarForm()
    fonteRmForm = RemoverFonteForm()
    peso_atual = get_last_peso(os.path.join(app.root_path,"logpesos.csv"))
    forms = {'bebidaForm':bebidaForm, 'pesoForm':pesoForm,'dinheiroForm':dinheiroForm, 'fonteAtivaForm':fonteAtivaForm, 'fonteRmForm':fonteRmForm}
    fontes = [{'imagem':url_for('static', filename=f'images/fontes/{fonte.image_file}'),
                'nome':fonte.nome,
                'quantidade':f'{fonte.atual}ml/{fonte.total}ml'} for fonte in Fonte.query.all() if fonte.available > 0]
    fontes_disponiveis = [{'imagem':url_for('static', filename=f'images/fontes/{fonte.image_file}'),
                'nome':fonte.nome,
                'idunique': f'{fonte.nome}{fonte.id}',
                'fonte_nm': idx+1,
                'cabo' : fonte.available,
                'quantidade':fonte.atual} for idx, fonte in enumerate(Fonte.query.all()) if fonte.available > 0]
    while (len(fontes) < 3):
        fontes += [{'imagem':url_for('static', filename='images/fontes/default.jpg'),
            'nome': 'Sem fonte cadastrada',
            'quantidade': '0ml/0ml'}]
    dinheiroForm.usuarios.choices = [("", "Escolha um cliente")] + [(i.username,i.username) for i in Usuario.query.all()]
    fonteRmForm.fontes.choices = [("", "Escolha uma fonte")] + [(i.nome,i.nome) for i in Fonte.query.all() if i.available > 0]

    if request.method == 'POST':
        if bebidaForm.validate_on_submit():
            if bebidaForm.picture.data:
                picture_file = save_picture(bebidaForm.picture.data, 'bebidas')
            else:
                picture_file = 'default.jpg'
            item = [['fonte1','quantidade_fonte1'], ['fonte2','quantidade_fonte2'],['fonte3','quantidade_fonte3']]
            fonte_pair = []
            for i in item:
                if bebidaForm[i[0]].data:
                    fonte_pair += [[f['nome'],int(bebidaForm[i[1]].data)]for f in fontes_disponiveis if f['fonte_nm'] == int(bebidaForm[i[0]].name[-1])]
            quantidades = []
            try:
                for fonte in fonte_pair:
                    d = {'fonte':Fonte.query.filter_by(nome=fonte[0]).first().id, 'exigido':fonte[1]}
                    qt = Quantidade(**d)
                    db.session.add(qt)
                    quantidades += [qt]
                db.session.commit()
            except:
                db.session.rollback()
                flash(f'Algum erro ocorreu no momento de cadastrar uma Quantidade!', 'danger')
                return redirect(url_for('heroes'))
            try:
                dic_bebida = {'nome':bebidaForm.nome_bebida.data, 'total': bebidaForm.custo_bebida.data,
                                'image_file': picture_file, 'available':1}
                for idx, q in enumerate(quantidades):
                    dic_bebida.update({f'quantidade{idx+1}':q.id})
                db.session.add(Bebida(**dic_bebida))
                db.session.commit()
            except:
                db.session.rollback()
                flash(f'Algum erro ocorreu no momento de cadastrar a Bebida!', 'danger')
                return redirect(url_for('heroes'))

            flash(f'Bebida cadastrada com sucesso!', 'success')
            return redirect(url_for('heroes'))
        elif bebidaForm.submitBebida.data:
            return render_template('heroes.html',peso_atual=peso_atual, bebidaClick=True, fontes=fontes, forms=forms, fontes_disponiveis=fontes_disponiveis)

        if forms['dinheiroForm'].validate_on_submit():
            try:
                userInst = Usuario.query.filter_by(username=forms["dinheiroForm"].usuarios.data)[0]
                userInst.dinheiro += forms["dinheiroForm"].dinheiro.data
                db.session.commit()
                flash(f'Adicionado {forms["dinheiroForm"].dinheiro.data} criptopontos para conta {forms["dinheiroForm"].usuarios.data}!', 'success')
            except:
                db.session.rollback()
                flash(f'Um erro ocorreu!','danger')
            return redirect(url_for('heroes'))
        elif dinheiroForm.submitDinheiro.data:
            return render_template('heroes.html',peso_atual=peso_atual, dinheiroClick=True, fontes=fontes, forms=forms, fontes_disponiveis=fontes_disponiveis)
        
        if pesoForm.validate_on_submit():
            
            try:
                file = os.path.join(app.root_path,"logpesos.csv")
                val = log_peso(pesoForm.userPeso.data, file)
                flash(f'O peso de {val}ml foi cadastrado com sucesso!','success')
            except:
                flash('Houve um erro na hora do cadastro', "danger")
            return redirect(url_for('heroes'))

        elif pesoForm.submitPeso.data:
            return render_template('heroes.html',peso_atual=peso_atual, pesoClick=True, fontes=fontes, forms=forms, fontes_disponiveis=fontes_disponiveis)
        if fonteAtivaForm.validate_on_submit():
            lista = [1,2,3]
            for i in fontes_disponiveis:
                lista.remove(i['cabo'])
            dic = {'nome':fonteAtivaForm.nome_fonte.data, 'total':fonteAtivaForm.atual.data,'atual':fonteAtivaForm.atual.data, 'available':lista[0]}
            if fonteAtivaForm.image_fonte.data:
                picture_file = save_picture(fonteAtivaForm.image_fonte.data, 'fontes')
            else:
                picture_file = 'default.jpg'    
            dic.update({'image_file':picture_file})
            db.session.add(Fonte(**dic))
            try:
                db.session.commit()
                flash(f'Fonte {forms["fonteAtivaForm"].nome_fonte.data} cadastrada com sucesso na mangueira {lista[0]}!', 'success')
            except:
                db.session.rollback()
                flash(f'Um erro ocorreu!','danger')
            return redirect(url_for('heroes'))
        elif fonteAtivaForm.submitAdicionarFonte.data:
            flash(f'Formulário não validado, cheque se há menos de três Fontes cadastradas!','danger')
            return render_template('heroes.html',peso_atual=peso_atual, ativaForm=True, fontes=fontes, forms=forms, fontes_disponiveis=fontes_disponiveis)
    
        if fonteRmForm.validate_on_submit():
            try:
                db.session.delete(Fonte.query.filter_by(nome=forms['fonteRmForm'].fontes.data).first())
                db.session.commit()
                flash(f"Fonte {forms['fonteRmForm'].fontes.data} removida!",'success')
            except:
                db.session.rollback()
                flash('Não foi possível remover a fonte', 'danger')
            return redirect(url_for('heroes'))
        elif fonteRmForm.submitRemoverFonte.data:
            return render_template('heroes.html',peso_atual=peso_atual, rmForm=True, fontes=fontes, forms=forms,fontes_disponiveis=fontes_disponiveis)

    return render_template('heroes.html',peso_atual=peso_atual, fontes=fontes, forms=forms, fontes_disponiveis=fontes_disponiveis)


@app.route("/app/finalizar", methods=['POST'])
@login_required
def finalizar():
    for i in request.form.items():
        bebida, valor = i
        if valor == 'submit':
            b = Bebida.query.filter_by(nome=bebida).first()
            try:
                current_user.dinheiro -=  b.total
                dic = {}
                try:
                    quantidade = Quantidade.query.filter_by(id=b.quantidade1).first()
                    fonte = Fonte.query.filter_by(id=quantidade.fonte).first()
                    dic.update({fonte.available:quantidade.exigido})
                    try:
                        fonte.atual -= quantidade.exigido
                        db.session.commit()
                    except:
                        db.session.rollback()
                        flash(f'Erro ao reduzir ml das fontes!', 'danger')
                except:
                    pass
                try:
                    quantidade = Quantidade.query.filter_by(id=b.quantidade2).first()
                    fonte = Fonte.query.filter_by(id=quantidade.fonte).first()
                    dic.update({fonte.available:quantidade.exigido})
                    try:
                        fonte.atual -= quantidade.exigido
                        db.session.commit()
                    except:
                        db.session.rollback()
                        flash(f'Erro ao reduzir ml das fontes!', 'danger')
                except:
                    pass
                try:
                    quantidade = Quantidade.query.filter_by(id=b.quantidade3).first()
                    fonte = Fonte.query.filter_by(id=quantidade.fonte).first()
                    dic.update({fonte.available:quantidade.exigido})
                    try:
                        fonte.atual -= quantidade.exigido
                        db.session.commit()
                    except:
                        db.session.rollback()
                        flash(f'Erro ao reduzir ml das fontes!', 'danger')
                except:
                    pass
                sorted_dict = dict(sorted(dic.items()))
                stt = ""
                for i in range(1,4):
                    if not(i in sorted_dict):
                        stt += "0;"
                    else:
                        stt+=f"{sorted_dict[i]/40};"
                stt = stt[:-1]
                bebida(stt)
            except:
                flash('Algum erro ocorreu!', 'danger')
                db.session.rollback()
                return redirect(url_for('album'))
        elif int(valor) > current_user.dinheiro:
            flash(f'Não possui criptomoedas suficientes!', 'danger')
            return redirect(url_for('album'))
    return render_template('finalizador.html', dinheiro=current_user.dinheiro, nome_bebida=bebida, valor=valor)

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
