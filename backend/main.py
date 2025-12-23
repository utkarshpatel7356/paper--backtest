from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pandas as pd
import re

# Import your modules
from src.parser.pdf_processor import convert_pdf_to_images
from src.parser.gemini_client import extract_strategy_from_images
from src.parser.generator import save_strategy_file
from src.backtester.engine import BacktestEngine

app = FastAPI(title="Alpha-Mechanism API")

# Enable CORS (allows your React App to talk to this Python Server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "input_papers")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Alpha-Mechanism AI is Running 🚀"}

@app.post("/analyze-paper/")
async def analyze_paper(file: UploadFile = File(...)):
    """
    PHASE 1: Upload PDF -> Extract Logic -> Save .py file
    """
    try:
        # 1. Save the uploaded file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📥 Received: {file.filename}")

        # 2. Run Phase 1 Pipeline
        images = convert_pdf_to_images(file_location)
        if not images:
            raise HTTPException(status_code=400, detail="Could not read PDF")
            
        strategy_data = extract_strategy_from_images(images)
        if not strategy_data:
            raise HTTPException(status_code=500, detail="Gemini failed to extract logic")
            
        # 3. Generate Code
        saved_path = save_strategy_file(strategy_data)
        
        return {
            "status": "success",
            "strategy_name": strategy_data['strategy_name'],
            "description": strategy_data['description'],
            "file_saved_at": saved_path
        }

    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/run-backtest/")
def run_backtest(strategy_name: str, ticker: str = "BTC-USD"):
    """
    PHASE 2: Run the generated strategy and return the equity curve
    """
    try:
        engine = BacktestEngine(start_date="2020-01-01", end_date="2023-12-31")
        
        # --- FIX: EXACT MATCH LOGIC ---
        # Do NOT remove the word "Strategy". Just clean symbols/spaces.
        # This matches generator.py logic perfectly.
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', strategy_name).lower()
        
        print(f"🔎 Request: '{strategy_name}' -> Looking for file: '{clean_name}.py'")
        
        results = engine.run(strategy_name=clean_name, ticker=ticker)
        
        if results is None or results.empty:
            raise HTTPException(status_code=404, detail="Backtest returned no data")
            
        # Fill NaNs
        results = results.fillna(1.0)

        # Chart Data
        chart_data = results[['cumulative_market', 'cumulative_strategy']].reset_index()
        chart_data.columns = ['date', 'market', 'strategy']
        chart_data['date'] = chart_data['date'].dt.strftime('%Y-%m-%d')
        
        final_return = results['cumulative_strategy'].iloc[-1] - 1
        
        return {
            "ticker": ticker,
            "total_return": f"{final_return:.2%}",
            "chart_data": chart_data.to_dict(orient="records")
        }
        
    except Exception as e:
        print(f"❌ Backtest Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))