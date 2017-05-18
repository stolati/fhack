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

    labels = db.relationship("Label", back_populates="data_class", lazy="dynamic")


class DataModel(db.Model):
    __tablename__ = "data_model"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, index=True)
    classes = db.relationship("DataClass", backref="model", lazy="dynamic")

    longname = db.Column(db.String)

    labels = db.relationship("Label", back_populates="model", lazy="dynamic")
    pending_labels = db.relationship("PendingLabel", back_populates="model", lazy="dynamic")


class Label(db.Model):
    __tablename__ = "label"
    __table_args__ = (
        db.UniqueConstraint("document_id", "position", "model_id"),
    )

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(db.ForeignKey("document.id"))
    position = db.Column(db.Integer)

    data_class_id = db.Column(db.ForeignKey("data_class.id"))
    data_class = db.relationship("DataClass", back_populates="labels")

    model_id = db.Column(db.ForeignKey("data_model.id"))
    model = db.relationship("DataModel", back_populates="labels")


class PendingLabel(db.Model):
    __tablename__ = "pending_label"
    __table_args__ = (
        db.UniqueConstraint("document_id", "position", "model_id"),
    )

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(db.ForeignKey("document.id"))
    document = db.relationship("Document", back_populates="pending_labels")

    position = db.Column(db.Integer)

    model_id = db.Column(db.ForeignKey("data_model.id"))
    model = db.relationship("DataModel", back_populates="pending_labels")

    responses = db.relationship("PendingLabelResponse", back_populates="pending_label")


class PendingLabelResponse(db.Model):
    __tablename__ = "pending_label_response"
    __table_args__ = (
        db.UniqueConstraint("pending_label_id", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)

    pending_label_id = db.Column(db.ForeignKey("pending_label.id"))
    pending_label = db.relationship("PendingLabel", back_populates="responses")

    user_id = db.Column(db.ForeignKey("user.id"))
    user = db.relationship("User", backref="pending_labels")

    data_class_id = db.Column(db.ForeignKey("data_class.id"))
    data_class = db.relationship("DataClass")


class Document(db.Model):
    __tablename__ = "document"

    id = db.Column(db.Integer, primary_key=True)

    path = db.Column(db.String)
    labels = db.relationship("Label", backref="document")
    pending_labels = db.relationship("PendingLabel", back_populates="document")


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)
