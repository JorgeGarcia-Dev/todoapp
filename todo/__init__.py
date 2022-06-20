import os


# Principal

# Importing the Flask class from the flask module.
from flask import Flask

# Crea una aplicación Flask, carga la configuración desde la carpeta de la instancia, inicializa el
# base de datos y registra el plano
# :return: El objeto de la aplicación

# Crea una instancia de la clase Flask y luego carga la configuración desde el archivo config.py
def create_app():
    # Crea una instancia de la clase Flask y luego carga la configuración desde el archivo config.py.
    app = Flask(__name__)
    
   # Cargando la configuración desde las variables de entorno.
    app.config.from_mapping(
        SECRET_KEY='#',
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE=os.environ.get('FLASK_DATABASE'),
    )
    
    # Importación de la variable db desde el módulo db.py.
    from . import db
    
    # Inicializa la base de datos con la aplicación.
    db.init_app(app)
    
    # Importación del modelo de autenticación desde el módulo de autenticación.
    from .import auth
    # Importación del modelo de autenticación desde el módulo de autenticación.
    from .import todo
    
    # Registra el plano en la aplicación.
    app.register_blueprint(auth.bp)
    # Registra el plano en la aplicación.
    app.register_blueprint(todo.bp)
    
    # Devuelve la cadena 'TodoER' cuando el usuario visita el URL /hola
    # :return: un String
    @app.route('/hola')
    def hola():
        return 'TodoER'
    
    # Devuelve el objeto de la aplicación.
    return app