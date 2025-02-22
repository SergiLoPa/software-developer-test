from prophet import Prophet
import calendar
from collections import defaultdict
from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
import pandas as pd
import io
import csv

app = FastAPI(title="Customer Purchases API")

# In-memory storage
purchases = []
filtered = []

class Purchase(BaseModel):
    """
    Schema for a customer purchase.

    Attributes:
    - customer_name: The name of the customer making the purchase.
    - country: The country of the customer.
    - purchase_date: The date when the purchase was made.
    - amount: The total amount spent by the customer.
    """
    customer_name: str
    country: str
    purchase_date: date
    amount: float

@app.post("/purchase/", response_model=Purchase)
async def add_purchase(purchase: Purchase):
    """
    Adds a new purchase to the in-memory storage.

    Args:
    - purchase: The purchase object.

    Returns:
    - The purchase object that was added.
    """
    purchases.append(purchase)
    return purchase

@app.post("/purchase/bulk/")
async def add_bulk_purchases(file: UploadFile = File(...)):
    """
    Adds multiple purchases from a CSV file to the in-memory storage.

    Args:
    - file: A CSV file containing multiple purchase records.

    Returns:
    - A JSON response indicating the number of purchases successfully added.
    
    Raises:
    - HTTPException: If the file is not a valid CSV file or if there is an error processing a row.
    """
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
    """
    Retrieves the list of purchases, with optional filtering by country and date range.

    Args:
    - countries: A list of country names to filter purchases.
    - start_date: The start date of the date range to filter purchases.
    - end_date: The end date of the date range to filter purchases.

    Returns:
    - A list of filtered purchase objects.
    """
    # In order to save the filtered purchases in the global variable
    global filtered
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
def calculate_kpis(kpi_option: str, days: int = 30):
    """
    Calculates and returns various KPIs related to customer purchases.

    Args:
    - kpi_option: A string specifying which data to use ("All purchases" or "Filtered purchases").

    Returns:
    - A dictionary containing the calculated KPIs such as mean purchase per client, 
      total revenue, clients per country, top countries by revenue, month with
      highest sales and forecast sales
    
    Raises:
    - HTTPException: If there are no purchases available for the selected KPI option.
    """
    if kpi_option == "All purchases":
        if not purchases:
            return {"error": "no purchases available"}
        purchases_set = purchases
    else:
        if not filtered:
            return {"error": "no filtered purchases available"}
        purchases_set = filtered
    
    # Initialize dictionaries to store data needed for KPIs
    clients = defaultdict(float)
    purchases_per_client = defaultdict(int)
    clients_per_country = defaultdict(int)
    revenue_per_country = defaultdict(float)
    sales_per_month = defaultdict(float)

    for purchase in purchases_set:
        clients_per_country[purchase.country] += 1
        clients[purchase.customer_name] += purchase.amount
        purchases_per_client[purchase.customer_name] += 1
        revenue_per_country[purchase.country] += purchase.amount
        # Extract the month and format it as a two-digit string
        month = purchase.purchase_date.strftime('%m')
        sales_per_month[month] += purchase.amount
    
    # Calculate the mean purchase per client
    mean_purchase_per_client = sum(clients.values()) / len(clients) if clients else 0

    # Calculate the total revenue from the purchases
    total_revenue = sum(purchase.amount for purchase in purchases_set)

    # Calculate the month with the highest sales
    top_month = max(sales_per_month, key=sales_per_month.get)
    top_month_sales = sales_per_month[top_month]
    # Convert month into a string
    top_month = calendar.month_name[int(top_month)]

    # Predict future sales using Prophet
    if len(purchases_set) > 2:
        df = pd.DataFrame([(p.purchase_date, p.amount) for p in purchases_set], columns=["ds", "y"])
        # Convert the "ds" column to datetime format for proper date handling
        df["ds"] = pd.to_datetime(df["ds"])
        # Group the data by date ("ds") and sum the amounts ("y") for each date, then reset the index
        df = df.groupby("ds").sum().reset_index()
        
        model = Prophet()
        model.fit(df)
        
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        # Get the last date in the original data to filter the forecasted results
        last_date = df["ds"].max()
        # Extract only the future forecasted data
        # Include the predicted values ("yhat") and confidence intervals ("yhat_lower", "yhat_upper")
        forecast_future = forecast[forecast["ds"] > last_date][["ds", "yhat", "yhat_lower", "yhat_upper"]]
    else:
        forecast_future = {"error": "more than two rows are required to predict sales"}
    
    return {
        "mean_purchase_per_client": mean_purchase_per_client,
        "total_revenue": total_revenue,
        "clients_per_country": clients_per_country,
        "top_countries_by_revenue": revenue_per_country,
        "top_month": {top_month: top_month_sales},
        "forecast_sales": forecast_future
    }
    