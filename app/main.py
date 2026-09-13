from fastapi import FastAPI, HTTPException
from app.services import LeadProcessor
from app.config import config
from app.utils import setup_logger

# Initialize logger
setup_logger()

# Validate config on startup
config.validate()

app = FastAPI(title="Lead Generation & Website Audit Agent")

@app.get("/")
def root():
    return {"message": "Lead Generation & Website Audit Agent is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/run")
def run_agent():
    try:
        processor = LeadProcessor()
        result = processor.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Process failed: {str(e)}")