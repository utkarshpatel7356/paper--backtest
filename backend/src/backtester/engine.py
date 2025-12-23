import pandas as pd
import numpy as np
import yfinance as yf
import importlib.util
import os
import sys

class BacktestEngine:
    def __init__(self, start_date="2020-01-01", end_date="2023-01-01"):
        self.start_date = start_date
        self.end_date = end_date

    def load_strategy(self, strategy_name):
        """
        Dynamically imports the generated strategy file.
        """
        # Construct path to generated strategy
        file_path = os.path.join("src", "strategies", "generated", f"{strategy_name}.py")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Strategy file not found: {file_path}")

        # Magic to import a file by path
        spec = importlib.util.spec_from_file_location("StrategyModule", file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["StrategyModule"] = module
        spec.loader.exec_module(module)
        
        # Find the class (assuming it ends with 'Strategy')
        for attribute_name in dir(module):
            if attribute_name.endswith("Strategy"):
                strategy_class = getattr(module, attribute_name)
                return strategy_class()
                
        raise ValueError("No class ending with 'Strategy' found in file.")

    def get_data(self, ticker):
        """
        Fetches daily data from Yahoo Finance.
        """
        print(f"📉 Fetching data for {ticker}...")
        df = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)
        
        # Flatten MultiIndex columns if necessary (yfinance update quirk)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Ensure we have a clean 'Close' column
        if 'Close' not in df.columns and 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
            
        return df

    def run(self, strategy_name, ticker="SPY"):
        """
        Main execution loop.
        """
        # 1. Load Strategy & Data
        strategy = self.load_strategy(strategy_name)
        df = self.get_data(ticker)
        
        if df.empty:
            print("❌ No data found.")
            return

        # --- FIX: Normalize columns to lowercase immediately ---
        df.columns = [c.lower() for c in df.columns]

        # 2. Run Strategy Logic
        print(f"🧠 Running {strategy_name} on {ticker}...")
        df = strategy.generate_signals(df)
        
        # --- FIX: Handle missing logic gracefully ---
        # If strategy crashed and returned empty DF, stop here
        if 'position' not in df.columns:
            print("⚠️ Strategy failed to generate 'position' column.")
            return None

        # 3. Calculate Returns (Using lowercase 'close')
        # Strategy Return = Position * Market Return (shifted to avoid lookahead)
        df['market_return'] = df['close'].pct_change()
        df['strategy_return'] = df['position'].shift(1) * df['market_return']
        
        # 4. Calculate Cumulative Metrics
        df['cumulative_market'] = (1 + df['market_return']).cumprod()
        df['cumulative_strategy'] = (1 + df['strategy_return']).cumprod()
        
        total_return = df['cumulative_strategy'].iloc[-1] - 1
        print(f"✅ Backtest Complete.")
        print(f"💰 Total Return: {total_return:.2%}")
        
        return df