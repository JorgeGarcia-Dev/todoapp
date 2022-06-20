from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

# Crea un Blueprint llamado 'todo'. Un Blueprint es una forma de organizar un grupo de vistas relacionadas y
# otro código. En lugar de registrar vistas y otro código directamente con una aplicación, son
# registrado con un plano. Luego, el plano se registra con la aplicación cuando se
# disponible en la función de fábrica.
bp = Blueprint('todo', __name__)

# Obtiene los todos de la base de datos y los pasa a la plantilla.
# :return: Una lista de diccionarios.
@bp.route('/')
# El decorador `@login_required` envuelve la función de vista `index()`. Cuando un usuario no ha iniciado sesión,
# Flask-Login guarda la URL de solicitud original en la sesión bajo la tecla `'siguiente'`. los
# El decorador `@login_required` luego redirige a la página de inicio de sesión, pasando la tecla `'siguiente'` como una consulta
# variable de cadena. Cuando el usuario inicia sesión correctamente, se le redirige a la URL `'siguiente'`.
@login_required
def index():
    # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
    # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
    db, c = get_db()
    # Una consulta SQL que selecciona todos los todos de la base de datos. El `%s` es un marcador de posición para el
    # `g.user['id']` valor.
    c.execute(
        'select t.id, t.description, u.username, t.completed, t.create_at from todo t JOIN user u on t.create_by = u.id where t.create_by = %s order by create_at desc', (g.user['id'],)
    )
    # `c.fetchall()` devuelve una lista de todas las filas en el conjunto de resultados.
    todos = c.fetchall()
    
    # La función `render_template()` invoca el motor de plantillas Jinja2 que es parte del Flask
    # estructura.
    # Jinja2 sustituye los bloques `{{ ... }}` con los valores correspondientes proporcionados como plantilla
    # argumentos.
    # La función `render_template()` representa la plantilla `todo/index.html`, pasando `todos`
    # lista como argumento de plantilla.
    return render_template('todo/index.html', todos=todos)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
# Si el método de solicitud es POST, obtenga la descripción del formulario, y si la descripción no es
# vacío, luego insértelo en la base de datos
# :return: una función render_template.
def create():
    # La sentencia `if` comprueba si el método de solicitud es `POST`. Si es así, el código en el bloque `si`
    # es ejecutado.
    if request.method == 'POST':
        # El objeto `request.form` es un diccionario que proporciona Flask para acceder a los datos del formulario enviados
        # por el usuario.
        description = request.form['description']
        # `error = Ninguno` es un marcador de posición para el mensaje de error. Si no hay error, el error
        # mensaje será `Ninguno`.
        error = None
        
        # Esto es comprobar si la descripción está vacía. Si es así, establecerá el mensaje de error.
        # a 'Descripción requerida.'
        if not description:
            error = 'Descripción es requerida.'
        # La función `flash()` almacena mensajes que se pueden recuperar al renderizar la plantilla.
        if error is not None:
            flash(error)
        else:
            # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
            # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
            db, c = get_db()
            # Insertar un nuevo todo en la base de datos.
            c.execute(
                'insert into todo (description, completed, create_by)'
                'values (%s, %s, %s)',
                (description, False, g.user['id'])
            )
            # `db.commit()` está confirmando los cambios en la base de datos.
            db.commit()
            # La función `redirect()` genera una respuesta de redirección a la URL dada. los
            # La función `url_for()` genera la URL para un punto final determinado.
            return redirect(url_for('todo.index'))
        
    # Renderizando la plantilla `todo/create.html`.
    return render_template('todo/create.html')

# Obtiene un todo de la base de datos por su id.
# :param id: El id del elemento pendiente para obtener
# :return: Una tupla con la información de tareas pendientes
def get_todo(id):
    # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
    # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
    db, c = get_db()
    # Insertar un nuevo todo en la base de datos.
    c.execute(
        'select t.id, t.description, t.completed, t.create_by, t.create_at, u.username from todo t JOIN user u on t.create_by = u.id where t.id = %s', (id,)
    )
    
    # `c.fetchone()` devuelve la primera fila del resultado de la consulta.
    todo = c.fetchone()
    
    # Si no se encuentra la tarea pendiente, la función se cancelará con un error 404.
    if todo is None:
        abort(404, "El todo de id {0} no existe" .format(id))
        
    # `return todo` está devolviendo el todo de la base de datos.
    return todo

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
# Obtiene el todo de la base de datos, verifica si el método de solicitud es POST y, si lo es, lo actualiza.
# el todo en la base de datos
# :param id: El id del elemento pendiente para actualizar
# :return: la plantilla 'todo/update.html' con la variable todo.
def update(id):
    # `get_todo(id)` está obteniendo el todo de la base de datos.
    todo = get_todo(id)
    
    # Esto es verificar si el método de solicitud es POST. Si es así, se ejecuta el código en el bloque if.
    if request.method == 'POST':
        # `request.form` es un diccionario que proporciona Flask para acceder a los datos enviados. los
        # La expresión `request.form['description']` está accediendo al valor del campo `description`
        # en el formulario enviado.
        description = request.form['description']
        # La expresión `request.form.get('completed')` está accediendo al valor de `completed`
        # campo en el formulario enviado. Si el campo `completado` está marcado, el valor será `'on'`.
        # Si el campo `completado` no está marcado, el valor será `Ninguno`. El `completado = Verdadero si
        # request.form.get('completed') == 'on' else False` expresión está comprobando si `completed`
        # campo está marcado. Si es así, el valor de `completed` será `True`. Si no lo es, el valor
        # de `completado` será `Falso`.
        completed = True if request.form.get('completed') == 'on' else False
        # `error = Ninguno` es un marcador de posición para el mensaje de error. Si no hay error, el error
        # mensaje será `Ninguno`.
        error = None
        
        # This is checking if the description is empty. If it is, it will set the error message to 'La
        # descripción es requerida.'
        if not description:
            error = "La descripción es requerida."
            
        # La función `flash()` almacena mensajes que se pueden recuperar al renderizar la plantilla.
        if error is not None:
            flash(error)
            
        # Esto es actualizar el todo en la base de datos.
        else:
            # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
            # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
            db, c = get_db()
            # Insertar un nuevo todo en la base de datos.
            c.execute(
                'update todo set description = %s, completed = %s'
                ' where id = %s and create_by = %s',
                (description, completed, id, g.user['id'])
            )
            # `db.commit()` está confirmando los cambios en la base de datos.
            db.commit()
            # Renderizando la plantilla `todo.index`.
            return redirect(url_for('todo.index'))
        
    # Representar la plantilla `todo/update.html` con la variable `todo`.
    return render_template('todo/update.html', todo=todo)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
# Elimina un elemento de tareas pendientes de la base de datos.
# :param id: El id del elemento pendiente para eliminar
# :return: una redirección a la url_for('todo.index')
def delete(id):
    # `get_db()` devuelve una conexión a la base de datos y un cursor. La conexión se utiliza para confirmar cambios.
    # a la base de datos. El cursor se utiliza para ejecutar consultas SQL.
    db, c = get_db()
    # Insertar un nuevo todo en la base de datos.
    c.execute('delete from todo where id = %s and create_by = %s', (id, g.user['id']))
    # `db.commit()` está confirmando los cambios en la base de datos.
    db.commit()
    # Renderizando la plantilla `todo.index`.
    return redirect(url_for('todo.index'))