from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import Usuario, Fonte
from app import bcrypt

def check_user(form, field):
    user = Usuario.query.filter_by(username=field.data).first()
    if not user:
        raise ValidationError('Selecione um Cliente válido')

class RegistrationForm(FlaskForm):
    def token_validator(form, field):
        if (field.data != "c0d849249c38dec0") and (len(field.data) != 0):
            raise ValidationError('Token incorreto!')
 
    def valid_username(form, field):
        user = Usuario.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Usuário já existe')

    username = StringField('Usuario', 
                            validators=[DataRequired(), Length(min=2, max=18), valid_username])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), Length(min=6, max=20), EqualTo('password')])
    admin = StringField('Token', validators=[token_validator])
    submit = SubmitField('Criar conta')

class LoginForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=18)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class BebidaForm(FlaskForm):
    def validate_click_bebida(form,field):
        if not form.submitBebida.data:
            raise ValidationError('Botão não selecionado')
    
    picture = FileField('Upload Imagem para Bebida', validators=[FileAllowed(['jpg','png','jpeg'])])
    submitBebida = SubmitField('Cadastrar', validators=[validate_click_bebida])

class PesoForm(FlaskForm):
    def validate_click_peso(form,field):
        if not form.submitPeso.data:
            raise ValidationError('Botão não selecionado')
    
    def number_validator(form, field):
        try:
            numb = int(form.userPeso.data)
            if numb < 0:
                raise ValidationError('Peso limite precisa ser um inteiro positivo')
        except:
            raise ValidationError('Apenas números inteiros são aceitos')

    userPeso = StringField('Peso limite de um copo (em ml)', validators=[DataRequired(), number_validator])
    submitPeso = SubmitField('Cadastrar', validators=[validate_click_peso])

class DinheiroForm(FlaskForm):
    def validate_click_dinheiro(form,field):
        if not form.submitDinheiro.data:
            raise ValidationError('Botão não selecionado') 

    def check_pwd(form, field):
        if current_user.admin == 0:
            raise ValidationError('Usuário não é administrador')
        elif not bcrypt.check_password_hash(current_user.password, form.senha.data):
            raise ValidationError('Senha incorreta')

    usuarios = SelectField('Usuários', choices=[], validators=[check_user])
    dinheiro = IntegerField('Valor', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20), check_pwd] )
    submitDinheiro = SubmitField('Pontuar', validators=[validate_click_dinheiro])

class RemoverFonteForm(FlaskForm):
    def validate_click_rm(form,field):
        if not form.submitRemoverFonte.data:
            raise ValidationError('Botão não selecionado') 

    def check_available(form, field):
        f = Fonte.query.filter_by(nome=form.fontes.data).first()
        if not f:
            raise ValidationError('Selecione uma fonte')
        elif not f.available:
            raise ValidationError('Fonte não ativa')

    fontes = SelectField('Fontes', choices=[], validators=[check_available])
    submitRemoverFonte = SubmitField('Remover', validators=[validate_click_rm])
    
class FontesAtivarForm(FlaskForm):
    def three_active(form, field):
        if Fonte.query.filter_by(available=1).count() >= 3:
            raise ValidationError('Já existem 3 fontes ativas.')
    def bound_check(form, field):
        if form.atual.data < 0 or form.atual.data > 4000:
            raise ValidationError(f'Valor {form.atual.data}ml está fora range esperado (0ml até 4000ml)')
    def validate_click_fonte(form, field):
        if not form.submitAdicionarFonte.data:
            raise ValidationError('Botão não selecionado') 
    
    nome_fonte = StringField('Nome da Fonte', validators=[DataRequired(), Length(min=4)])
    image_fonte = FileField('Upload Imagem para Fonte', validators=[FileAllowed(['jpg','png','jpeg'])])
    atual = IntegerField('Quantidade na Garrafa em ml', validators=[DataRequired(), bound_check])
    submitAdicionarFonte = SubmitField('Cadastro', validators=[three_active, validate_click_fonte])

class FontesRemoverForm(FlaskForm):
    def check_fontes(form, field):
        f = Fonte.query.filter_by(nome=field.data).first()
        if not f:
            raise ValidationError('Selecione uma fonte válida')
        elif f.available == 0:
            raise ValidationError('Fonte não estava ativa')
    def validate_click_fonte_rem(form, field):
        if not form.submitRemoveForm.data:
            raise ValidationError('Botão não selecionado')
    fontes = SelectField('Fontes', choices=[], validators=[check_fontes])
    submitRemoveForm = SubmitField('Remover', validators=[validate_click_fonte_rem])
    