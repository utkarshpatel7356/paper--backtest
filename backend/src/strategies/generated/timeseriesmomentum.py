
import pandas as pd
import numpy as np
import pandas_ta as ta

class TimeSeriesMomentumStrategy:
    '''
    This strategy capitalizes on the time-series momentum anomaly. It goes long assets that have exhibited positive returns over the past 12 months (approximately 252 trading days) and shorts assets that have shown negative returns over the same period.
    Target Universe: A diversified universe of liquid assets, including equity indices, currencies, commodities, and sovereign bonds, typically traded via futures contracts.
    '''
    
    def __init__(self):
        self.lookback = 252
        self.required_columns = ['close']
        
    def generate_signals(self, df: pd.DataFrame):
        '''
        Applies logic to the dataframe.
        '''
        # 1. Normalize Columns
        df = df.copy()
        df.columns = [c.lower() for c in df.columns] 
        
        # 2. Define Helper Variables
        lookback = self.lookback
        if 'risk_free_rate' not in df.columns: df['risk_free_rate'] = 0.0
        
        # 3. Pre-Initialize Position
        df['position'] = 0
        
        # 4. Run AI Logic
        try:
            # Entry Logic
            signal = 1 if data['close'].pct_change(lookback_period).iloc[-1] > 0 else 0
            
            # Exit Logic (Optional)
            signal = -1 if data['close'].pct_change(lookback_period).iloc[-1] < 0 else 0
            
            pass # Ensures the try block is never empty
        except Exception as e:
            print(f"Error in strategy logic: {e}")
            return df
            
        # 5. Map Synonyms to 'entry_signal'
        if 'target_position' in df.columns: df['entry_signal'] = df['target_position']
        if 'long_entry' in df.columns:
            df['entry_signal'] = 0
            df.loc[df['long_entry'] == True, 'entry_signal'] = 1
            if 'short_entry' in df.columns:
                 df.loc[df['short_entry'] == True, 'entry_signal'] = -1
        
        # 6. Apply Signal to Position
        if 'entry_signal' in df.columns:
            if df['entry_signal'].dtype == 'bool':
                df.loc[df['entry_signal'] == True, 'position'] = 1
            else:
                df['position'] = df['entry_signal']
        
        # 7. Apply Exits
        if 'exit_signal' in df.columns:
            mask = (df['exit_signal'] == 1) | (df['exit_signal'] == True)
            df.loc[mask, 'position'] = 0
            
        # 8. Clean up and Hold
        df['position'] = df['position'].replace(0, np.nan).ffill().fillna(0)
        
        return df
