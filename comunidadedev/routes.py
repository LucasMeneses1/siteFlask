from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from comunidadedev import app, database, bcrypt
from comunidadedev.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormPost, FormComentar
from comunidadedev.models import Usuario, Post, Comentario
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
from flask_cors import cross_origin
import cloudinary
import cloudinary.uploader
import cloudinary.api
from io import BytesIO


@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)

@app.route('/usuario/<usuario_id>')
@login_required
def usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    posts = Post.query.filter_by(id_usuario=usuario_id).all()
    return render_template('usuario.html', usuario=usuario, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.encode('utf-8'), form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash('{} logado com sucesso!'.format(current_user.username), 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash('Falha no Login. E-mail ou Senha Incorretos!', 'alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript, foto_perfil = url_for('static', filename='fotos_perfil/default.jpg'))
        database.session.add(usuario)
        database.session.commit()
        usuario = Usuario.query.filter_by(email=form_criarconta.email.data).first()
        login_user(usuario, remember=form_login.lembrar_dados.data)
        flash('Conta no {} criada com sucesso!'.format(form_criarconta.email.data), 'alert-success')
        return redirect(url_for('editar_perfil'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout realizado com sucesso!', 'alert-success')
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = current_user.foto_perfil
    return render_template('perfil.html', foto_perfil=foto_perfil)

@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form_post = FormPost()
    if form_post.validate_on_submit():
        post = Post(titulo=form_post.titulo.data, corpo=form_post.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form_post=form_post)


def salvar_imagem(imagem):
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    buf = BytesIO()
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(buf, 'jpeg')
    buf.seek(0)
    image_bytes = buf.read()
    buf.close()
    upload_cloud = cloudinary.uploader.upload(image_bytes)
    link = jsonify(upload_cloud)
    url = link.json
    return url['url']


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    if len(lista_cursos) == 0:

        return 'Não Informado'
    else:
        return ';'.join(lista_cursos)



@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
@cross_origin()
def editar_perfil():
    form_editarperfil = FormEditarPerfil()
    if form_editarperfil.validate_on_submit():
        current_user.email = form_editarperfil.email.data
        current_user.username = form_editarperfil.username.data
        if form_editarperfil.foto_perfil.data:
            nome_imagem = salvar_imagem(form_editarperfil.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form_editarperfil)
        database.session.commit()
        flash('Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form_editarperfil.email.data = current_user.email
        form_editarperfil.username.data = current_user.username
    foto_perfil = current_user.foto_perfil
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form_editarperfil=form_editarperfil)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    comentarios = Comentario.query.filter_by(id_post=post_id)
    form_comentar = FormComentar()
    if form_comentar.validate_on_submit():
        comentario = Comentario(corpo=form_comentar.corpo.data, id_post=post_id, id_usuario=current_user.id)
        database.session.add(comentario)
        database.session.commit()
        flash('Comentário realizado com sucesso!', 'alert-success')
        return redirect(url_for('exibir_post', post_id=post_id))
    return render_template('post.html', post=post, comentarios=comentarios, form_comentar=form_comentar)


@app.route('/post/<post_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form_editarpost = FormPost()
        if request.method == 'GET':
            form_editarpost.titulo.data = post.titulo
            form_editarpost.corpo.data = post.corpo
        elif form_editarpost.validate_on_submit():
            post.titulo = form_editarpost.titulo.data
            post.corpo = form_editarpost.corpo.data
            database.session.commit()
            flash('Post atualizado com sucesso!', 'alert-success')
            return redirect(url_for('exibir_post', post_id=post_id))

    else:
        form_editarpost = None
    return render_template('editar_post.html', post=post, form_editarpost=form_editarpost)



@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso!', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)

@app.route('/comentario/<comentario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_comentario(comentario_id):
    comentario = Comentario.query.get(comentario_id)
    form_editarcomentario = FormComentar()
    if request.method == 'GET':
        form_editarcomentario.corpo.data = comentario.corpo
    elif form_editarcomentario.validate_on_submit():
        comentario.corpo = form_editarcomentario.corpo.data
        database.session.commit()
        flash('Comentário atualizado com sucesso!', 'alert-success')
        return redirect(url_for('exibir_post', post_id=comentario.id_post))

    else:
        form_editarpost = None
    return render_template('editar_comentario.html', comentario=comentario, form_editarcomentario=form_editarcomentario)



@app.route('/comentario/<comentario_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_comentario(comentario_id):
    comentario = Comentario.query.get(comentario_id)
    if current_user == comentario.autor:
        database.session.delete(comentario)
        database.session.commit()
        flash('Comentário excluído com sucesso!', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')