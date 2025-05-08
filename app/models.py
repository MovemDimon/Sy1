from app.core import db


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    gateway = db.Column(db.String, nullable=False)
    currency = db.Column(db.String, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    fee = db.Column(db.Numeric, nullable=True)
    signature = db.Column(db.String, nullable=True)
    tx_hash = db.Column(db.String, nullable=True)
    confirm_count = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
