from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Setting(Base):
    __tablename__ = "setting"

    name = Column(String(64), nullable=False, unique=True, primary_key=True)
    type = Column(String(32), nullable=False)
    value = Column(String, nullable=False)
