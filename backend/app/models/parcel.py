from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Numeric,
    DateTime,
    func,
)

from app.db.database import Base


class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)

    # Parcel Identification
    parcel_number = Column(String(50), unique=True, nullable=False, index=True)
    gpin = Column(String(50), unique=True, nullable=True, index=True)

    # Property Address
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))

    # Owner Information
    owner_name = Column(String(255))
    mailing_address = Column(String(255))

    # Property Characteristics
    zoning = Column(String(50))
    lot_size = Column(Float)

    # Assessment
    land_value = Column(Numeric(12, 2))
    improvement_value = Column(Numeric(12, 2))
    total_assessment = Column(Numeric(12, 2))

    # GIS
    latitude = Column(Float)
    longitude = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )