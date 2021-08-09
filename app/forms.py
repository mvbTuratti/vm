from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import Usuario

def token_validator(form, field):
    if (field.data != "c0d849249c38dec0") and (len(field.data) != 0):
        raise ValidationError('Token incorreto!')

def valid_username(form, field):
    user = Usuario.query.filter_by(username=field.data).first()
    if user:
        raise ValidationError('Usuário já existe')


def validate_click_peso(form,field):
    if not form.submitPeso.data:
        raise ValidationError('Botão não selecionado')

def validate_click_bebida(form,field):
    if not form.submitBebida.data:
        raise ValidationError('Botão não selecionado')    

class RegistrationForm(FlaskForm):
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
    picture = FileField('Upload Imagem para Bebida', validators=[FileAllowed(['jpg','png','jpeg'])])
    submitBebida = SubmitField('Cadastrar', validators=[validate_click_bebida])

class PesoForm(FlaskForm):
    userPeso = StringField('User', validators=[DataRequired(), Length(min=4)])
    submitPeso = SubmitField('Cadastrar', validators=[validate_click_peso])