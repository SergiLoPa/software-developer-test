import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import StringIO

API_BASE_URL = "http://localhost:8000"

st.title(":shopping_bags: Customer Purchases Dashboard")

tab1, tab2 = st.tabs(["Upload Purchases", "Analyze Data"])

# Upload Purchases Tab
with tab1:
    st.header("Upload Purchases from CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        if st.button("Confirm Upload", type="primary"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            response = requests.post(f"{API_BASE_URL}/purchase/bulk/", files=files)
            if response.status_code == 200:
                st.success("CSV uploaded successfully!")
            else:
                st.error("Error uploading CSV.")

    st.header("Add a Single Purchase")
    with st.form("purchase_form"):
        customer_name = st.text_input("Customer Name")
        country = st.text_input("Country")
        purchase_date = st.date_input("Purchase Date")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        submit_button = st.form_submit_button("Submit Purchase")
    
    if submit_button:
        data = {
            "customer_name": customer_name,
            "country": country,
            "purchase_date": purchase_date.isoformat(),
            "amount": amount,
        }
        response = requests.post(f"{API_BASE_URL}/purchase/", json=data)
        if response.status_code == 200:
            st.success("Purchase added successfully!")
        else:
            st.error("Error adding purchase.")

# Analyze Data Tab
with tab2:
    st.header("Filter Purchases")
    country_filter = st.text_input("Country (optional)")
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)
    
    query_params = {}
    if country_filter:
        query_params["country"] = country_filter
    if start_date:
        query_params["start_date"] = start_date.isoformat()
    if end_date:
        query_params["end_date"] = end_date.isoformat()
    
    if st.button("Get Purchases"):
        response = requests.get(f"{API_BASE_URL}/purchases/", params=query_params)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.info("No purchases found.")
        else:
            st.error("Error fetching purchases.")

    st.header("Compute KPIs")
    if st.button("Compute KPIs"):
        response = requests.get(f"{API_BASE_URL}/purchases/kpis")
        if response.status_code == 200:
            kpis = response.json()
            st.subheader("🛒📊 Mean purchase per client:")
            st.text(kpis["mean_purchase_per_client"])

            st.subheader("🌍👥 Number of clients per country")
            df = pd.DataFrame(list(kpis["clients_per_country"].items()), columns=["Country", "Number of Clients"])
            st.dataframe(df, hide_index=True, width=400)
            fig = px.choropleth(
                df,
                locations="Country",
                locationmode="country names",
                color="Number of Clients",
                color_continuous_scale="Reds",
            )
            st.plotly_chart(fig)
        else:
            st.error("Error fetching KPIs.")
