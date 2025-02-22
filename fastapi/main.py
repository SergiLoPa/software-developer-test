from collections import defaultdict
from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
import io
import csv

app = FastAPI(title="Customer Purchases API")

# In-memory storage
purchases = []

class Purchase(BaseModel):
    customer_name: str
    country: str
    purchase_date: date
    amount: float

@app.post("/purchase/", response_model=Purchase)
async def add_purchase(purchase: Purchase):
    purchases.append(purchase)
    return purchase

@app.post("/purchase/bulk/")
async def add_bulk_purchases(file: UploadFile = File(...)):
    if file.content_type not in ["text/csv"]:
        raise HTTPException(status_code=400, detail="Invalid file format")
    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    new_purchases = []
    for row in reader:
        try:
            purchase = Purchase(
                customer_name=row["customer_name"],
                country=row["country"],
                purchase_date=date.fromisoformat(row["purchase_date"]),
                amount=float(row["amount"])
            )
            purchases.append(purchase)
            new_purchases.append(purchase)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing row: {row} - {e}")
    return JSONResponse(content={"added": len(new_purchases)})

@app.get("/purchases/", response_model=List[Purchase])
def get_purchases(countries: Optional[List[str]] = Query(None), start_date: Optional[date] = None, end_date: Optional[date] = None):
    filtered = purchases
    if countries:
        countries_lower = [c.lower() for c in countries]
        filtered = [p for p in filtered if p.country.lower() in countries_lower]
    if start_date:
        filtered = [p for p in filtered if p.purchase_date >= start_date]
    if end_date:
        filtered = [p for p in filtered if p.purchase_date <= end_date]
    return filtered

@app.get("/purchases/kpis")
def calculate_kpis():
    if not purchases:
        return {"error": "no purchases available"}
    
    clients = defaultdict(float)
    clients_per_country = defaultdict(int)

    for purchase in purchases:
        clients_per_country[purchase.country] += 1
        clients[purchase.customer_name] += purchase.amount
    
    mean_purchase_per_client = sum(clients.values()) / len(clients) if clients else 0
    
    return {
        "mean_purchase_per_client": mean_purchase_per_client,
        "clients_per_country": clients_per_country
    }
    