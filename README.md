# 🛒 Customer Purchases API & Streamlit App

A system to manage and analyze customer purchases, built with **FastAPI** (backend) and **Streamlit** (frontend), and containerized with **Docker**.

---

## 🚀 Features

### Backend (FastAPI)
- **Add a single purchase**: `POST /purchase/`
- **Bulk upload purchases**: `POST /purchase/bulk/` (CSV file)
- **Filter purchases**: `GET /purchases/` (by date and country)
- **Compute KPIs**: `GET /purchases/kpis` (mean purchases per client, clients per country)

### Frontend (Streamlit)
- **Upload Tab**:
  - CSV file upload for bulk purchases.
  - Form for single purchase entry.
- **Analyze Tab**:
  - Filter purchases by date and country.
  - Display KPIs.

## 🛠️ Getting Started

### Prerequisites
- [Docker desktop](https://www.docker.com/products/docker-desktop) installed.

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
2. Build and run the containers:
   ```bash
   docker-compose up --build
   
## 🌐 Acces the Applications

| Service      | URL                              |
|--------------|----------------------------------|
| **FastAPI**  | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Streamlit**| [http://localhost:8501](http://localhost:8501)          |

## 🧪 Testing

Unit tests have been written for the backend functionality. Here's how to run them:

### Steps to Run Tests

1. **Enter the FastAPI container**:
   ```bash
   docker exec -it fastapi /bin/bash
2. **Run the tests**:
   ```bash
   python -m pytest
