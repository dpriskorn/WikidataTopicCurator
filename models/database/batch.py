from app import db


class Batch(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    qid = db.Column(db.Text, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    to_be_matched = db.Column(db.Integer, nullable=False)
