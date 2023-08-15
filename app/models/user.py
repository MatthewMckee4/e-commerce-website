from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, text


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    shipping_address = Column(String(200))
    date_created = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User id={self.id}, name={self.name}>"
