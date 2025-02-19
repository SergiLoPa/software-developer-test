from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

CSV_FILE_PATH = "../sample_purchases.csv"

def test_add_bulk_purchases():
    with open(CSV_FILE_PATH, "rb") as file:
        response = client.post("/purchase/bulk/", files={"file": ("sample_purchases.csv", file, "text/csv")})
    print("Response JSON", response.json())
    assert response.status_code == 200
    assert "added" in response.json()
    