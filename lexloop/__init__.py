import os
from flask import Flask,render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', #set to api or randdom key when deploying & set config.py file
        DATABASE=os.path.join(app.instance_path, 'lexloop.sqlite'),
        UPLOADS=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('dashboard/welcome.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp) 
    
    from . import upload
    app.register_blueprint(upload.bp)

    from . import process
    app.register_blueprint(process.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)


    return app