from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidadedev.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome do usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro email ou faça login para continuar')

class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome do usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    curso_html = BooleanField('HTML')
    curso_css = BooleanField('CSS')
    curso_javascript = BooleanField('JavaScript')
    curso_python = BooleanField('Python')
    curso_sql = BooleanField('SQL')
    curso_java = BooleanField('Java')
    botao_submit_editarperfil = SubmitField('Salvar')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado!')


class FormPost(FlaskForm):
    titulo = StringField(validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu post aqui', validators=[DataRequired()])
    botao_submit_post = SubmitField('Criar Post')


class FormComentar(FlaskForm):
    corpo = TextAreaField('Escreva seu comentário aqui:', validators=[DataRequired()])
    botao_submit_comentar = SubmitField('Comentar')
