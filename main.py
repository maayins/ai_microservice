# FastAPI entry point
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import requests
import numpy as np
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

@app.post("/sql", response_model=PromptResponse)
def process_prompt(req: SqlRequest):
    sql = req.sql.lower()                

    return PromptResponse(result=run_suite_ql_http_client(sql,))



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
