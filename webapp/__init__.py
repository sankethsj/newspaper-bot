from flask import Flask

from .models import DB_NAME, create_database, db


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    create_database(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
