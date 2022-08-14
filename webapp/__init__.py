from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
