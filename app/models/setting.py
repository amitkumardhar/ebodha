from sqlalchemy import Column, String
from app.db.base_class import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True) # JSON encoded or simple string
