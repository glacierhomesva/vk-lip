from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.parcel import Parcel


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    parcel_number = Column(String(50), ForeignKey("parcels.parcel_number"), index=True, nullable=False)
    tax_year = Column(Integer, nullable=False)
    land_value = Column(Numeric(12, 2))
    improvement_value = Column(Numeric(12, 2))
    total_value = Column(Numeric(12, 2))

    parcel = relationship("Parcel", back_populates="assessments")
