from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from statistics import mean
import numpy as np

app = FastAPI()

# Allow POST requests from anywhere (important!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load telemetry data
def load_telemetry():
    try:
        # Try to load from data.json in the same directory
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except:
        return []

TELEMETRY_DATA = load_telemetry()

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
def check_latency(data: RequestBody):
    results = {}
    
    for region in data.regions:
        # Filter data for this region
        region_data = [record for record in TELEMETRY_DATA if record.get('region') == region]
        
        if not region_data:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        # Extract latency and uptime values
        latencies = [record['latency_ms'] for record in region_data]
        uptimes = [record['uptime_pct'] for record in region_data]
        
        # Calculate metrics
        avg_latency = mean(latencies)
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = mean(uptimes)
        breaches = sum(1 for lat in latencies if lat > data.threshold_ms)
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }
    
    return {"regions": results}
