from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Numeric,
    Text,
    DateTime,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)

    # Parcel Identification
    parcel_number = Column(String(50), unique=True, nullable=False, index=True)
    gpin = Column(String(50), nullable=True, index=True)

    # Parcel Address
    street_number = Column(String(20), nullable=True, index=True)
    street_name = Column(String(255), nullable=True, index=True)
    unit = Column(String(50), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)

    # Owner Information
    owner_name = Column(String(255))
    owner_address = Column(String(255))
    owner_city_state = Column(String(255))
    owner_zip_code = Column(String(20))
    mailing_address = Column(String(255))

    # Property Characteristics
    zoning = Column(String(50))
    property_type = Column(String(100), nullable=True)
    neighborhood = Column(String(100), nullable=True, index=True)
    lot_size = Column(Float)
    years_owned = Column(Integer, nullable=True)
    sia_flag = Column(Boolean, nullable=True, default=False)
    developer_owned = Column(Boolean, nullable=True, default=False)
    adjacent_developer_owned = Column(Boolean, nullable=True, default=False)
    tax_delinquent = Column(Boolean, nullable=True, default=False)
    tax_lien_amount = Column(Numeric(12, 2), nullable=True)
    tax_delinquency_remarks = Column(Text, nullable=True)

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

    assessments = relationship(
        "Assessment",
        back_populates="parcel",
        cascade="all, delete-orphan",
    )