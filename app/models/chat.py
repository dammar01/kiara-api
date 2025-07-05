from sqlalchemy import Column, Integer, DateTime, String
from app.core.database import Base


class Chat(Base):
    __tablename__ = "chat"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    questions = Column(String)
    answers = Column(String, nullable=True)
