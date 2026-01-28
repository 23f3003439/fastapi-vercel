from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow POST requests from anywhere (important!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
def check_latency(data: RequestBody):
    return {
        "received_regions": data.regions,
        "threshold": data.threshold_ms
    }
