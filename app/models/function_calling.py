from sqlalchemy import Column, Integer, String
from app.core.database import Base


class FunctionCalling(Base):
    __tablename__ = "function_calling"
    id = Column(Integer, primary_key=True, index=True)
    questions_id = Column(Integer)
    function_name = Column(String)
    arguments = Column(String)
