from src.backtester.engine import BacktestEngine
import matplotlib.pyplot as plt

def main():
    # 1. Initialize Engine
    engine = BacktestEngine(start_date="2015-01-01", end_date="2023-12-31")
    
    # 2. Run the generated strategy
    # Note: The file name you showed me was 'timeseriesmomentum.py', 
    # so the strategy_name arg must match that filename (without .py)
    results = engine.run(strategy_name="timeseriesmomentum", ticker="BTC-USD")
    
    # 3. Simple Plot
    if results is not None:
        plt.figure(figsize=(10, 6))
        plt.plot(results['cumulative_market'], label='Buy & Hold (Bitcoin)', linestyle='--')
        plt.plot(results['cumulative_strategy'], label='AI Strategy (TS Momentum)', linewidth=2)
        plt.title("AI Strategy vs Market")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    main()