from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

CSV_FILE_PATH = "../sample_purchases.csv"

def test_add_purchase():
    response = client.post(
        "/purchase/", 
        json={
            "customer_name": "John Cruise",
            "country": "United States of America",
            "purchase_date": "2024-06-02",
            "amount": 365.25,
        },
    )
    assert response.status_code == 200
    assert response.json()["customer_name"] == "John Cruise"

def test_add_bulk_purchases():
    with open(CSV_FILE_PATH, "rb") as file:
        response = client.post("/purchase/bulk/", files={"file": ("sample_purchases.csv", file, "text/csv")})
    assert response.status_code == 200
    assert "added" in response.json()

def test_get_purchases_no_filter():
    response = client.get("/purchases/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_purchases_by_country():
    response = client.get("/purchases/?country=United States of America")
    assert response.status_code == 200
    assert response.json() != []
    assert all(purchase["country"] == "United States of America" for purchase in response.json())

def test_calculate_kpis():
    response = client.get("purchases/kpis/")
    assert response.status_code == 200
    assert "mean_purchase_per_client" in response.json()
    