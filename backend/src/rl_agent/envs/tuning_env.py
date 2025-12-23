import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces

class StrategyTuningEnv(gym.Env):
    """
    Custom Environment where the Agent learns to tune the 'lookback' parameter
    of a strategy based on market volatility.
    """
    def __init__(self, strategy_class, df, initial_balance=10000):
        super(StrategyTuningEnv, self).__init__()
        
        self.strategy = strategy_class()
        self.df = df
        self.initial_balance = initial_balance
        
        # Action Space: The Agent chooses a lookback period between 3 and 60 days
        # We map Discrete(58) -> 3..60
        self.action_space = spaces.Discrete(58) 
        
        # Observation Space: [Recent Volatility, Recent Return, Current Lookback]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)
        
        self.current_step = 60 # Start after enough data exists
        self.balance = initial_balance
        self.positions = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 60
        self.balance = self.initial_balance
        self.positions = 0
        return self._get_observation(), {}

    def _get_observation(self):
        # Look at the last 30 days window
        window = self.df.iloc[self.current_step-30 : self.current_step]
        
        volatility = window['Close'].pct_change().std()
        recent_return = (window['Close'].iloc[-1] / window['Close'].iloc[0]) - 1
        current_lookback = self.strategy.lookback
        
        return np.array([volatility, recent_return, current_lookback], dtype=np.float32)

    def step(self, action):
        # 1. Agent adjusts the strategy (Action 0 -> Lookback 3)
        new_lookback = action + 3 
        self.strategy.lookback = new_lookback
        
        # 2. Get Data Slice for Strategy Logic
        # We need enough history for the NEW lookback to work
        slice_start = self.current_step - new_lookback - 1
        data_slice = self.df.iloc[slice_start : self.current_step + 1].copy()
        
        # 3. Ask Strategy: "Buy or Sell?"
        # We modify the strategy instance to use the new lookback
        processed_df = self.strategy.generate_signals(data_slice)
        
        # Get the signal for the *current* timestep (the last row)
        position = processed_df['position'].iloc[-1]
        
        # 4. Step Market Forward
        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            terminated = True
            market_return = 0
        else:
            terminated = False
            # Calculate PnL for holding this position for 1 day
            current_price = self.df['Close'].iloc[self.current_step-1]
            next_price = self.df['Close'].iloc[self.current_step]
            market_return = (next_price - current_price) / current_price
            
        # 5. Calculate Reward (Daily Profit)
        daily_reward = position * market_return * 100 # Scale up for RL stability
        
        self.balance *= (1 + (position * market_return))
        
        info = {"balance": self.balance, "lookback": new_lookback}
        
        return self._get_observation(), daily_reward, terminated, False, info