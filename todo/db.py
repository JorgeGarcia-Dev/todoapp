import mysql.connector

import click

from flask import current_app, g 
from flask.cli import with_appcontext
from .schema import instructions

# Si no hay una conexión de base de datos en la variable global `g`, cree una y guárdela en `g`
# :return: Una tupla de la conexión a la base de datos y el cursor.
def get_db():
    # Está comprobando si hay una conexión de base de datos en la variable global `g`. Si no lo hay, es
    # crea uno y lo guarda en `g`.
    if 'db' not in g:
        # Está creando una conexión a la base de datos.
        g.db = mysql.connector.connect(
            host=current_app.config['DATABASE_HOST'],
            user=current_app.config['DATABASE_USER'],
            password=current_app.config['DATABASE_PASSWORD'],
            database=current_app.config['DATABASE']
        )
        
        # Está creando un objeto de cursor que se usará para ejecutar sentencias SQL.
        g.c = g.db.cursor(dictionary=True)
    # Devolviendo una tupla de la conexión a la base de datos y el cursor.
    return g.db, g.c 

# Si hay una conexión a la base de datos, ciérrela".
    
# La función comienza obteniendo la conexión de la base de datos desde el contexto de la aplicación. Si no hay
# conexión de base de datos, la función regresa inmediatamente
    
# :param e: La excepción que se planteó, si la hubo
def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
# Crea una conexión de base de datos, crea un cursor y ejecuta las instrucciones SQL en el
# lista de `instrucciones`
def init_db():
    db, c = get_db()
    
    for i in instructions:
        c.execute(i)
        
    db.commit()
    
# Es un decorador que define un comando de línea de comando llamado `init_db`
@click.command('init_db')
@with_appcontext

# Crea una tabla de base de datos llamada entradas, que tiene dos columnas: título y texto.
def init_db_command():
    init_db()
    click.echo('Base de datos inicializada')

# Le dice a Flask que llame a esa función cuando limpie después de devolver la respuesta
# :param app: La instancia de la aplicación Flask
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)