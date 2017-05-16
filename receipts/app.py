from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = Flask(__name__)
manager = Manager(app)


def init_app(extra_config=None):
    app.config.from_object("receipts.settings")

    if extra_config:
        app.config.update(extra_config)

    from .models import db
    db.app = app
    db.init_app(app)

    migrate = Migrate(app, db)
    manager.add_command("db", MigrateCommand)

    return app
