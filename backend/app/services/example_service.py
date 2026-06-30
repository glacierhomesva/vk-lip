from sqlalchemy.orm import Session
from app.models.example import Example


def get_examples(db: Session):
    return db.query(Example).all()
