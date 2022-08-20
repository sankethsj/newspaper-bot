import os

from flask_sqlalchemy import SQLAlchemy

DB_NAME = "epaper.db"

db = SQLAlchemy()

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(128))
    region_code = db.Column(db.String(128))
    date = db.Column(db.String(128))
    paper_code = db.Column(db.String(128))


def create_database(app):
    if not os.path.exists('webapp/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
