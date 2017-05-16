from flask_sqlalchemy import SQLAlchemy, Model


class Base(Model):
    @classmethod
    def get_or_create(cls, **params):
        ret = cls.query.filter_by(**params).first()
        if not ret:
            ret = cls(**params)
            db.session.add(ret)
        return ret


db = SQLAlchemy(model_class=Base, session_options={"autocommit": True})


class DataClass(db.Model):
    __tablename__ = "data_class"
    __table_args__ = (
        db.UniqueConstraint("classno", "model_id"),
    )

    id = db.Column(db.Integer, primary_key=True)

    classno = db.Column(db.Integer)
    name = db.Column(db.String)
    model_id = db.Column(db.ForeignKey("data_model.id"))


class DataModel(db.Model):
    __tablename__ = "data_model"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, index=True)
    classes = db.relationship("DataClass", backref="model")


class Label(db.Model):
    __tablename__ = "label"
    __table_args__ = (
        db.UniqueConstraint("document_id", "position"),
    )

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(db.ForeignKey("document.id"))
    position = db.Column(db.Integer)

    data_class_id = db.Column(db.ForeignKey("data_class.id"))
    data_class = db.relationship("DataClass")


class Disagreement(db.Model):
    __tablename__ = "disagreement"
    __table_args__ = (
        db.UniqueConstraint("model_id", "document_id", "position"),
    )

    id = db.Column(db.Integer, primary_key=True)

    position = db.Column(db.Integer)
    document_id = db.Column(db.ForeignKey("document.id"))
    model_id = db.Column(db.ForeignKey("data_model.id"))
    responses = db.Column(db.String)

    document = db.relationship("Document")
    model = db.relationship("DataModel")


class PendingLabel(db.Model):
    __tablename__ = "pending_label"

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(db.ForeignKey("document.id"))
    position = db.Column(db.Integer)

    data_class_id = db.Column(db.ForeignKey("data_class.id"))
    data_class = db.relationship("DataClass")

    user_id = db.Column(db.ForeignKey("user.id"))
    user = db.relationship("User", backref="pending_labels")


class Document(db.Model):
    __tablename__ = "document"

    id = db.Column(db.Integer, primary_key=True)

    path = db.Column(db.String)
    labels = db.relationship("Label", backref="document")


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
