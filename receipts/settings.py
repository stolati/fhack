import os

module_dir = os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.dirname(module_dir)
db_path = os.path.join(base_dir, "receipts.db")

APP_NAME = "Receipt Labeling Service"

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(db_path)
SQLALCHEMY_TRACK_MODIFICATIONS = False

del module_dir, base_dir, db_path
