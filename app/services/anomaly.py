# Anomaly detection logic
import numpy as np

def detect_anomalies(data):
    try:
        row = [float(x) for x in data[0]]  # Assume first row is numeric
        mean = np.mean(row)
        std = np.std(row)
        anomalies = []

        for i, value in enumerate(row):
            if abs(value - mean) > 2 * std:
                anomalies.append((i, value))  # index and value

        if anomalies:
            return [["Index", "Anomaly Value"]] + [[i, v] for i, v in anomalies]
        else:
            return [["No tp anomalies detected"]]
    except Exception as e:
        return [["Error"], [f"Anomaly detection failed: {str(e)}"]]
