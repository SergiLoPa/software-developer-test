import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import pycountry

# Fetch a list of all country names using pycountry for dropdowns or filters
countries = [country.name for country in pycountry.countries]
# Adapted United States to United States of America in order to match our sample_purchases.csv
countries = [country.replace("United States", "United States of America") for country in countries]

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
        # Verify that customer name and country are not empty
        if not customer_name.strip():
            st.error("Customer Name cannot be empty!")
        elif not country.strip():
            st.error("Country cannot be empty!")
        else:
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
        query_params["countries"] = country_filter
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

    # Form to choose purchases set and change number of days predicted
    with st.form("kpis_form"):
        option_purchases = st.radio(
        "Which set of purchases do you want to use?",
        ["All purchases", "Filtered purchases"],
        )
        days_forecast_sales = st.number_input("How many days do you want to predict?", min_value=1, value=30)
        compute_kpis = st.form_submit_button("Compute KPIs")
    params = {"kpi_option": option_purchases, "days": days_forecast_sales}

    if compute_kpis:
        response = requests.get(f"{API_BASE_URL}/purchases/kpis", params=params)
        if response.status_code == 200:
            kpis = response.json()
            if "error" in kpis:
                st.info(kpis["error"])
            else:
                # Display KPIs such as total revenue, mean purchase per client and month with the highest sales
                st.subheader("📊 KPIs")
                st.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
                st.metric("Mean Purchase per Client", f"${kpis["mean_purchase_per_client"]:,.2f}")

                month_name, total_sales = list(kpis['top_month'].items())[0]
                st.metric("Month with Highest Sales", value=month_name, delta=f"${total_sales:,.2f}")

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

                # Sort the countries by total spending in descending order and select the top 10
                top_countries = sorted(kpis['top_countries_by_revenue'].items(), key=lambda x: x[1], reverse=True)[:10]
                countries = [country for country, _ in top_countries]
                spending = [amount for _, amount in top_countries]
                # Create a bar chart showing the total spending for the top 10 countries
                fig = px.bar(x=countries, y=spending, labels={'x': 'Country', 'y': 'Total Spending ($)'}, 
                title='Top 10 Countries by Spending', color=spending, color_continuous_scale='Reds')
                st.plotly_chart(fig)

                # Forecast sales
                if "error" not in kpis["forecast_sales"]:
                    st.subheader("📈🔮 Forecast sales")
                    # Convert the forecast sales data into a pandas DataFrame
                    forecast_df = pd.DataFrame(kpis["forecast_sales"])
                    st.write(forecast_df)
                    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])
                    # Create a Plotly line chart for the forecasted sales (yhat) over time (ds)
                    fig = px.line(forecast_df, x="ds", y="yhat", title="Forecast Sales",
                                labels={"ds": "Date", "yhat": "Predicted Sales"})
                    # Add lower and upper confidence intervals (yhat_lower and yhat_upper) to the plot
                    fig.add_traces([
                    px.line(forecast_df, x="ds", y="yhat_lower", labels={"ds": "Date", "yhat_lower": "Lower Bound"}).data[0],
                    px.line(forecast_df, x="ds", y="yhat_upper", labels={"ds": "Date", "yhat_upper": "Upper Bound"}).data[0]
                    ])
                    st.plotly_chart(fig)
                else:
                    st.info(kpis["forecast_sales"]["error"])


        else:
            st.error("Error fetching KPIs.")
