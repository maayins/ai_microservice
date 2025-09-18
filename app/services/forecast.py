# Forecast logic
import numpy as np
from sklearn.linear_model import LinearRegression

def forecast_logic(data):
    try:
        row = [float(x) for x in data[0]]  # Assume first row is numeric time series
        x = np.arange(len(row)).reshape(-1, 1)
        model = LinearRegression().fit(x, row)
        next_val = model.predict([[len(row)]])[0]
        return [["Forecast"], [round(next_val, 2)]]
    except Exception as e:
        return [["Error"], [f"Forecasting failed: {str(e)}"]]
