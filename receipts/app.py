import os

from flask import Flask

module_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(module_dir)
db_path = os.path.join(base_dir, "receipts.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(db_path)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

