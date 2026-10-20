from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Numeric)
