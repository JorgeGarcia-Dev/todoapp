import functools

from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)

from werkzeug.security import check_password_hash, generate_password_hash

from todo.db import get_db

# Crea un Blueprint llamado 'auth' que tiene su url_prefix establecido en /auth.
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
# Comprueba si el método de solicitud es POST, y si lo es, obtiene el nombre de usuario y la contraseña del
# formulario, comprueba si el nombre de usuario ya existe, y si no es así, inserta el nombre de usuario y hash
# contraseña en la base de datos
# :return: Una función que toma un nombre de usuario y una contraseña y devuelve un usuario si es válido.
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
        # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
        db, c = get_db()
        error = None
        # Una consulta SQL que selecciona todos los todos de la base de datos. El `%s` es un marcador de posición para el
        # `g.user['id']` valor.
        c.execute(
            'select id from user where username = %s', (username,)
        )
        # Si no ingresa nombre de usuario, manda el error "Username es requerido"
        if not username:
            error = 'Username es requerido'
            # Si no ingresa password, manda el error "Password es requerido"
        if not password:
            error = 'Password es requerido'
        # Esto es verificar si el nombre de usuario ya está en la base de datos.
        elif c.fetchone() is not None:
            error = 'Usuario {} se encuentra registrado.'.format(username)
            
        # Esto es insertar el nombre de usuario y la contraseña en la base de datos.
        if error is None:
            # Insertar un nuevo todo en la base de datos.
            c.execute(
                'insert into user (username, password) values (%s, %s)',
                (username, generate_password_hash(password))
            )
            # `db.commit()` está confirmando los cambios en la base de datos.
            db.commit()
            
            # Redirigir al usuario a la página de inicio de sesión.
            return redirect(url_for('auth.login'))
        
        flash(error)
    # # Renderizando la plantilla `auth/register.html`.    
    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])

# Obtiene el nombre de usuario y la contraseña del formulario enviado, comprueba si existe el nombre de usuario y si el
# la contraseña coincide, y si es así, inicia la sesión del usuario
# :return: Una plantilla con el formulario de inicio de sesión.
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
        # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
        db, c = get_db()
        error = None
        # Una consulta SQL que selecciona todos los todos de la base de datos. El `%s` es un marcador de posición para el
        # `g.user['id']` valor.
        c.execute(
            'select * from user where username = %s', (username,)
        )
        # Esto es verificar si el nombre de usuario ya está en la base de datos.
        user = c.fetchone()
        
        # Esto es verificar si el nombre de usuario está en la base de datos.
        if user is None:
            error = 'Usuario y/o contraseña inválida'
        # Esto es verificar si la contraseña es correcta.
        elif not check_password_hash(user['password'], password):
            error = 'Usuario y/o contraseña inválida'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('todo.index'))
        
        flash(error)
        
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        db, c = get_db()
        c.execute(
            'select * from user where id = %s', (user_id,)
        )
        g.user = c.fetchone()
        
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))