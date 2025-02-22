import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import pycountry

# Fetch a list of all country names using pycountry for dropdowns or filters
countries = [country.name for country in pycountry.countries]

# Base URL for the FastAPI backend
API_BASE_URL = "http://fastapi:8000"

st.title(":shopping_bags: Customer Purchases Dashboard")

# Sidebar configuration with instructions and app description
st.sidebar.title("📊 Customer Purchases App")

st.sidebar.markdown(
    """
    **How to use**  
    1️⃣ Upload a CSV file with purchase data.  
    2️⃣ Analyze KPIs and trends.  
    3️⃣ Visualize insights with interactive charts.  
    """
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    **About**  
    🛒 *Customer Purchases App* helps you manage and analyze customer transactions efficiently.  
    Gain insights on purchase behavior, track KPIs, and explore data visually.  
    """
)

tab1, tab2 = st.tabs(["Upload Purchases", "Analyze Data"])

# Upload Purchases Tab
with tab1:
    st.header("Upload Purchases from CSV")
    # File uploader for CSV files
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        # Read the uploaded CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        # Button to confirm and upload the CSV to the backend
        if st.button("Confirm Upload", type="primary"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            response = requests.post(f"{API_BASE_URL}/purchase/bulk/", files=files)
            if response.status_code == 200:
                st.success("CSV uploaded successfully!")
            else:
                st.error("Error uploading CSV.")

    # Form to add a single purchase manually
    st.header("Add a Single Purchase")
    with st.form("purchase_form"):
        customer_name = st.text_input("Customer Name")
        country = st.text_input("Country")
        purchase_date = st.date_input("Purchase Date")
        amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
        submit_button = st.form_submit_button("Submit Purchase")
    
    # Handle form submission for single purchase
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
    # Multiselect dropdown for filtering by country
    country_filter = st.multiselect("Select the countries (optional)", countries, default=[], placeholder="Choose one or more countries")
    # Date pickers for filtering by date range
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)
    
    query_params = {}
    if country_filter:
        query_params["country"] = country_filter
    if start_date:
        query_params["start_date"] = start_date.isoformat()
    if end_date:
        query_params["end_date"] = end_date.isoformat()
    
    # Button to fetch filtered purchases from the backend
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

    # Section to compute and display KPIs
    st.header("Compute KPIs")
    if st.button("Compute KPIs"):
        response = requests.get(f"{API_BASE_URL}/purchases/kpis")
        if response.status_code == 200:
            kpis = response.json()
            # Display mean purchase per client
            st.subheader("🛒📊 Mean purchase per client:")
            st.text(kpis["mean_purchase_per_client"])

            # Display number of clients per country in a table and choropleth map
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
