from sqlalchemy.sql import text
from datetime import date

from app import db


class FinishedItem(db.Model):
    qid = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    date = db.Column(
        db.Date,
        nullable=False,
        default=date.today(),
        server_default=text("CURRENT_DATE"),
    )
