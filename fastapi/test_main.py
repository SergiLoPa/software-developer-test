from datetime import date
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

CSV_FILE_PATH = "/app/sample_purchases.csv"

def test_add_purchase():
    """
    Test the POST /purchase/ endpoint for adding a single purchase.
    Verifies that the response status code is 200 (success) and that
    the customer name in the response matches the one sent in the request.
    """
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
    """
    Test the POST /purchase/bulk/ endpoint for adding multiple purchases
    from a CSV file. Verifies that the response status code is 200 (success)
    and that the response contains the key "added" indicating successful processing.
    """
    with open(CSV_FILE_PATH, "rb") as file:
        response = client.post("/purchase/bulk/", files={"file": ("sample_purchases.csv", file, "text/csv")})
    assert response.status_code == 200
    assert "added" in response.json()

def test_get_purchases_no_filter():
    """
    Test the GET /purchases/ endpoint without any filters.
    Verifies that the response status code is 200 (success) and that
    the response is a list of purchases.
    """
    response = client.get("/purchases/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_purchases_by_country():
    """
    Test the GET /purchases/ endpoint with a country filter.
    Verifies that the response status code is 200 (success), that the
    response is not empty, and that all purchases in the response
    belong to the specified country ("United States of America").
    """
    response = client.get("/purchases/?countries=United States of America")
    assert response.status_code == 200
    assert response.json() != []
    assert all(purchase["country"] == "United States of America" for purchase in response.json())

def test_get_purchases_by_date_range():
     """
    Test the GET /purchases/ endpoint with a date range filter.
    Verifies that the response status code is 200 (success) and that
    all purchases in the response fall within the specified date range
    (from January 1, 2024, to December 31, 2024).
    """
     response = client.get("/purchases/?start_date=2024-01-01&end_date=2024-12-31")
     assert response.status_code == 200
     assert all(
         date.fromisoformat(purchase["purchase_date"]) >= date(2024, 1, 1) and
         date.fromisoformat(purchase["purchase_date"]) <= date(2024, 12, 31)
         for purchase in response.json()
     )

def test_calculate_kpis():
    """
    Test the GET /purchases/kpis/ endpoint for calculating KPIs.
    Verifies that the response status code is 200 (success) and that
    the response contains the key "mean_purchase_per_client", which
    is expected to be part of the KPI calculation.
    """
    response = client.get("purchases/kpis/?kpi_option=All+purchases")
    assert response.status_code == 200
    assert "mean_purchase_per_client" in response.json()
    