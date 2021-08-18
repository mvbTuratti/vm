from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(18), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    admin = db.Column(db.Integer, nullable=False)
    dinheiro = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"User('{self.username}')"

class Fonte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(18), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    atual = db.Column(db.Integer, nullable=False, default=total)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    available = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Fonte('{self.nome}','{self.atual}'/'{self.total}', '{self.image_file}', available={self.available})"
    
class Quantidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fonte = db.Column(db.Integer, db.ForeignKey('fonte.id'), nullable=False)
    exigido = db.Column(db.Integer, nullable=False)
    drinks = db.relationship("Fonte", foreign_keys=[fonte])
    

class Bebida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(18), unique=True, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    available = db.Column(db.Integer, nullable=False)
    quantidade1 = db.Column(db.Integer, db.ForeignKey('quantidade.id'))
    quantidade2 = db.Column(db.Integer, db.ForeignKey('quantidade.id'))
    quantidade3 = db.Column(db.Integer, db.ForeignKey('quantidade.id'))
    componente1 = db.relationship("Quantidade", foreign_keys=[quantidade1])
    componente2 = db.relationship("Quantidade", foreign_keys=[quantidade2])
    componente3 = db.relationship("Quantidade", foreign_keys=[quantidade3])
    
    
class Vendas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bebida = db.Column(db.Integer, db.ForeignKey('bebida.id'), nullable=False)
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    bebida_id_key = db.relationship("Bebida", foreign_keys=[bebida])
    usuario_id_key = db.relationship("Usuario", foreign_keys=[usuario])
