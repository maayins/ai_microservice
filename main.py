# FastAPI entry point
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import requests
import numpy as np
import pyodbc

from sklearn.linear_model import LinearRegression

# 🔹 Import services
from app.services.forecast import forecast_logic
from app.services.anomaly import detect_anomalies
from app.services.netsuite_service import run_suite_ql_http_client

app = FastAPI(title="AI/ML Microservice for Excel ERP Insights")

# Input/Output models
class PromptRequest(BaseModel):
    prompt: str
    data: Union[List[List[Union[str, float]]], None] = None

# Input/Output models
class SqlRequest(BaseModel):
    query: str

class PromptResponse(BaseModel):
    result: List[List[Union[str, float]]]

@app.get("/transactions")
def get_transactions(limit: int = 5):
    try:
        # Connect to NetSuite ODBC
        conn = pyodbc.connect(f"DSN=NetSuite;UID=netsuite.webservice@biobridgeglobal.org;PWD=BBGNetsuite@2025")
        cursor = conn.cursor()

        # Run SQL query
        query = f"SELECT TOP 10 * from transaction"
        cursor.execute(query)

        # Fetch column names
        columns = [col[0] for col in cursor.description]

        # Fetch all rows and map into dicts
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]

        conn.close()

        return {"data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main Endpoint
@app.post("/process", response_model=PromptResponse)
def process_prompt(req: PromptRequest):
    prompt = req.prompt.lower()

    if "forecast" in prompt:
        if not req.data:
            raise HTTPException(status_code=400, detail="Data is required for forecasting.")
        return PromptResponse(result=forecast_logic(req.data))

    elif any(kw in prompt for kw in ["anomaly", "detect outliers", "detect anomalies"]):
        if not req.data:
            raise HTTPException(status_code=400, detail="Data is required for anomaly detection.")
        return PromptResponse(result=detect_anomalies(req.data))

    elif "overdue" in prompt or "aging" in prompt:
        return PromptResponse(result=analyze_ar_aging_from_dotnet())    

    return PromptResponse(result=[["Unsupported prompt. Try: 'Forecast sales', 'Detect anomalies', 'Check overdue invoices'."]])

@app.post("/sql")
def process_prompt(req: SqlRequest):
    try:
        sql = req.query.lower()                

        return run_suite_ql_http_client(sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# AR aging logic
def analyze_ar_aging_from_dotnet():
    try:
        dotnet_api_url = "http://localhost:5000/api/ar-aging"
        response = requests.get(dotnet_api_url, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

        flagged = [["Customer", "Overdue Days"]]
        for record in raw_data:
            overdue = float(record.get("overdue_days", 0))
            if overdue > 90:
                flagged.append([record.get("customer_name", "Unknown"), overdue])

        return flagged if len(flagged) > 1 else [["No Overdue > 90 days found."]]
    except Exception as e:
        return [["Error"], [str(e)]]
