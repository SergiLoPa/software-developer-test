# 🛒 Customer Purchases API & Streamlit App

A system to manage and analyze customer purchases, built with **FastAPI** (backend) and **Streamlit** (frontend), and containerized with **Docker**.

---
## ⚙️ System Architecture

The system follows a **client-server architecture** with the following components:

- **Frontend (Streamlit)**: Provides a user interface for data upload and KPI analysis.
- **Backend (FastAPI)**: Handles API requests, processes purchases, and computes KPIs.
- **Storage**: Purchases are stored in memory (extendable to a database).
- **Docker**: Both frontend and backend are containerized for easy deployment.


## 🧑‍💻 File structure
```bash
├── fastapi/
│   ├── main.py                # FastAPI app and API endpoints
│   ├── test_main.py           # Unit tests for FastAPI app
│   ├── sample_purchases.csv   # Sample purchases for testing
│   ├── requirements.txt       # Backend dependencies
│   └── Dockerfile             # Dockerfile for FastAPI
├── streamlit/
│   ├── app.py                 # Streamlit app for UI
│   ├── requirements.txt       # Frontend dependencies
│   └── Dockerfile             # Dockerfile for Streamlit
├── docker-compose.yml         # Docker Compose file to run both services
```
## 🚀 Features

### Backend (FastAPI)
✅ **Add a single purchase** – `POST /purchase/`  
✅ **Bulk upload purchases** – `POST /purchase/bulk/` (CSV file)  
✅ **Filter purchases** – `GET /purchases/` (by date and country)  
✅ **Compute KPIs** – `GET /purchases/kpis`  

### **Frontend (Streamlit)**
📂 **Upload Tab**  
   - Upload purchases via CSV.  
   - Add a single purchase manually.

📊 **Analyze Tab**  
   - Filter purchases by date and country.  
   - View key KPIs and customer distribution.

## 📊 **Key Performance Indicators (KPIs)**

| **KPI**                           | **Description**                                                                                                                                                          |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **💰 Mean Purchase per Client**   | Average amount spent by each client.                                                                                                                                      |
| **📈 Total Revenue**              | Total sum of all revenue generated from purchases.                                                                                                                         |
| **🌍 Clients per Country**        | Number of clients from each country.                                                                                                                                      |
| **🏆 Top Countries by Revenue**   | Countries that contribute the most to total revenue.                                                                                                                     |
| **📅 Month with Highest Sales**   | The month with the highest sales volume.                                                                                                                                  |
| **🔮 Forecast Sales using Prophet** | Future sales projections using the **Prophet** algorithm.                                                                                                                  |


## 🛠️ Getting Started

### Prerequisites
Ensure you have **Docker Desktop** installed:  
🔗 [Download Docker](https://www.docker.com/products/docker-desktop) 

### Installation
1️⃣ **Clone the repo**:

```bash
git clone https://github.com/SergiLoPa/software-developer-test.git
cd software-developer-test
```

2️⃣ **Build and run the containers**:
   ```bash
   docker-compose up --build
   ```
## 🌐 Acces the Applications

| Service      | URL                              |
|--------------|----------------------------------|
| **FastAPI**  | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Streamlit**| [http://localhost:8501](http://localhost:8501)          |

## 🧪 Testing

Unit tests have been written for the backend functionality. Here's how to run them:

### Steps to Run Tests

1️⃣ **Enter the FastAPI container**:
   ```bash
   docker exec -it software-developer-test-fastapi-1 /bin/bash
   ```
2️⃣ **Run the tests**:
   ```bash
   python -m pytest
   ```

### 🚀 _Ready to track and analyze customer purchases efficiently!_
