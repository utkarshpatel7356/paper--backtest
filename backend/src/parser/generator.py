import os
import re

TEMPLATE = """
import pandas as pd
import numpy as np
import pandas_ta as ta

class {class_name}:
    '''
    {description}
    Target Universe: {universe}
    '''
    
    def __init__(self):
        self.lookback = {lookback}
        self.required_columns = {columns}
        
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
            {entry_logic}
            
            # Exit Logic (Optional)
            {exit_logic}
            
            pass # Ensures the try block is never empty
        except Exception as e:
            print(f"Error in strategy logic: {{e}}")
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
"""

def save_strategy_file(data, output_dir="src/strategies/generated"):
    if not data:
        return

    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Sanitize Strategy Name (Remove special chars, limit length)
    raw_name = data.get('strategy_name', 'UnknownStrategy')
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', raw_name) # Remove spaces/symbols
    clean_name = clean_name[:50] # Hard limit to 50 chars
    
    class_name = clean_name + "Strategy"
    filename = clean_name.lower() + ".py"
    filepath = os.path.join(output_dir, filename)
    
    # 2. Fill Template with .get() safety
    code = TEMPLATE.format(
        class_name=class_name,
        description=data.get('description', 'No description'),
        universe=data.get('asset_universe', 'Unknown'),
        lookback=data.get('lookback_period', 14),
        columns=data.get('required_columns', []),
        entry_logic=data.get('entry_logic', 'False'),
        exit_logic=data.get('exit_logic', 'False')
    )
    
    with open(filepath, "w") as f:
        f.write(code)
        
    print(f"✅ Strategy Created: {filepath}")
    return filepath