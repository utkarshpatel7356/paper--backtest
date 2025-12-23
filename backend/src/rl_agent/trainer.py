import pandas as pd
import yfinance as yf
from stable_baselines3 import PPO
from src.rl_agent.envs.tuning_env import StrategyTuningEnv
from backend.src.strategies.generated.timeseriesmomentumtsmom import TimeSeriesMomentumStrategy

def train_agent():
    # 1. Get Training Data
    print("📉 Fetching Training Data (BTC-USD)...")
    df = yf.download("BTC-USD", start="2018-01-01", end="2022-01-01", progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 2. Initialize Environment
    # We pass the class (not instance) so the Env can create fresh ones
    env = StrategyTuningEnv(TimeSeriesMomentumStrategy, df)
    
    # 3. Setup PPO Agent
    print("🧠 Initializing PPO Agent...")
    model = PPO("MlpPolicy", env, verbose=1)
    
    # 4. Train
    print("🚀 Starting Training Loop (10,000 steps)...")
    model.learn(total_timesteps=10000)
    
    # 5. Save the Brain
    model.save("ppo_momentum_tuner")
    print("✅ Model Saved as 'ppo_momentum_tuner.zip'")

def test_agent():
    # Load separate testing data
    print("\n📉 Fetching Test Data (2022-2024)...")
    df_test = yf.download("BTC-USD", start="2022-01-02", end="2024-01-01", progress=False)
    if isinstance(df_test.columns, pd.MultiIndex):
        df_test.columns = df_test.columns.get_level_values(0)
        
    env = StrategyTuningEnv(TimeSeriesMomentumStrategy, df_test)
    model = PPO.load("ppo_momentum_tuner")
    
    obs, _ = env.reset()
    done = False
    
    print("🎮 Running Live Test...")
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, truncated, info = env.step(action)
        
        # Print periodically to show it's "thinking"
        if env.current_step % 100 == 0:
            print(f"Step {env.current_step}: Agent chose Lookback={info['lookback']} days. Balance=${info['balance']:.0f}")

if __name__ == "__main__":
    train_agent()
    test_agent()