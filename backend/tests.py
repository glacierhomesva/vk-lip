from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
