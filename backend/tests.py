from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.imports.import_tax_delinquency import _parcel_number_from_row, _read_rows
from app.main import app
from app.models.parcel import Parcel

client = TestClient(app)


def test_tax_delinquency_reader_skips_report_preamble(tmp_path):
    report = tmp_path / "report.csv"
    report.write_text(
        "CITY OF CHARLOTTESVILLE,,,,\n"
        ",,,,\n"
        "Account ,Current Owner Name,Property Address,,,PIN #,Status,Notes,,\n"
        '44624,"ZELLER, TROY WAYNE",2323 HIGHLAND AVE,,,210115100,A,$1000/mo,,\n',
        encoding="utf-8",
    )

    rows = list(_read_rows(str(report)))

    assert len(rows) == 1
    assert _parcel_number_from_row(rows[0]) == "210115100"


def test_tax_delinquency_reader_supports_pin_header_alias():
    row = {"PIN #": "210115100"}

    assert _parcel_number_from_row(row) == "210115100"


def set_parcel_delinquency(
    db: Session,
    parcel_number: str,
    tax_delinquent: bool,
    lien_amount: float | None,
) -> tuple[bool | None, object | None]:
    parcel = db.query(Parcel).filter(Parcel.parcel_number == parcel_number).first()
    if parcel is None:
        raise AssertionError(f"Missing fixture parcel: {parcel_number}")
    original = (parcel.tax_delinquent, parcel.tax_lien_amount)
    parcel.tax_delinquent = tax_delinquent
    parcel.tax_lien_amount = lien_amount
    db.commit()
    return original


def test_get_parcel_with_latest_assessment():
    response = client.get("/parcels/010001000")
    assert response.status_code == 200

    data = response.json()
    assert data["parcel_number"] == "010001000"
    assert data["address"] == "1117 EMMET ST N"
    assert data["zoning"] == "NX-10"
    assert float(data["lot_size"]) == 39.77

    latest = data.get("latest_assessment")
    assert latest is not None
    assert latest["tax_year"] == 2026
    assert float(latest["land_value"]) == 50266600.0
    assert float(latest["improvement_value"]) == 116477200.0
    assert float(latest["total_value"]) == 166743800.0


def test_opportunities_endpoint_default():
    response = client.get("/opportunities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "parcel_number" in item
        assert "address" in item
        assert "owner" in item
        assert "owner_address" in item
        assert "owner_city_state" in item
        assert "owner_zip_code" in item
        assert "zoning" in item
        assert "acres" in item
        assert "absentee_owner" in item
        assert item["zoning"] in {"R-A", "R-B", "R-C", "RN-A", "RX-3", "RX-5"}


def test_opportunities_endpoint_filter_parcel_number():
    response = client.get("/opportunities?parcel_number=010007000")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["parcel_number"] == "010007000"


def test_get_vacant_land_property_type():
    response = client.get("/parcels/010008000")
    assert response.status_code == 200

    data = response.json()
    assert data["parcel_number"] == "010008000"
    assert data["property_type"] == "Vacant Land"


def test_opportunities_endpoint_filter_min_sqft():
    response = client.get("/opportunities?min_sqft=500000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    for item in data:
        assert item["acres"] >= (500000 / 43560.0)


def test_opportunities_endpoint_filter_zoning():
    response = client.get("/opportunities?zoning=R-A")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_opportunities_endpoint_filter_zoning_min_acres():
    response = client.get("/opportunities?zoning=R-A&min_acres=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_opportunities_endpoint_absentee_only():
    response = client.get("/opportunities?absentee_only=true")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_opportunities_endpoint_adjacent_developer_owned_only():
    response = client.get("/opportunities?adjacent_developer_owned_only=true")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert item["adjacent_developer_owned"] is True


def test_opportunities_endpoint_sorted_by_vk_score():
    response = client.get("/opportunities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if len(data) > 1:
        scores = [item["vk_score"] for item in data]
        assert scores == sorted(scores, reverse=True)

    for item in data:
        assert "vk_score" in item
        assert isinstance(item["vk_score"], int)


def test_opportunities_tax_delinquent_only_filter():
    db = SessionLocal()
    parcel_number = "010007000"
    original_state = set_parcel_delinquency(db, parcel_number, True, 4200.0)

    try:
        response = client.get(f"/opportunities?parcel_number={parcel_number}&tax_delinquent_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["parcel_number"] == parcel_number
        assert data[0]["tax_delinquent"] is True
    finally:
        set_parcel_delinquency(db, parcel_number, original_state[0] or False, original_state[1])
        db.close()


def test_opportunities_min_tax_lien_amount_filter():
    db = SessionLocal()
    parcel_number = "010007000"
    original_state = set_parcel_delinquency(db, parcel_number, True, 1500.0)

    try:
        response = client.get(f"/opportunities?parcel_number={parcel_number}&min_tax_lien_amount=2000")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        response = client.get(f"/opportunities?parcel_number={parcel_number}&min_tax_lien_amount=1000")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["parcel_number"] == parcel_number
    finally:
        set_parcel_delinquency(db, parcel_number, original_state[0] or False, original_state[1])
        db.close()


def test_opportunities_suggested_offer_range_filter():
    parcel_number = "010007000"

    response = client.get(f"/opportunities?parcel_number={parcel_number}")
    assert response.status_code == 200
    base_data = response.json()
    assert len(base_data) == 1
    suggested_offer = base_data[0]["suggested_offer"]
    assert suggested_offer is not None

    response = client.get(
        f"/opportunities?parcel_number={parcel_number}&min_suggested_offer={suggested_offer - 1}&max_suggested_offer={suggested_offer + 1}",
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["parcel_number"] == parcel_number

    response = client.get(
        f"/opportunities?parcel_number={parcel_number}&min_suggested_offer={suggested_offer + 1000}",
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
