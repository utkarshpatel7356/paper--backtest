import os
import json
import google.generativeai as genai
import typing_extensions as typing
from dotenv import load_dotenv
from src.parser.validator import LogicValidator

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Strict Schema
class StrategySchema(typing.TypedDict):
    strategy_name: str
    description: str
    asset_universe: str
    lookback_period: int
    required_columns: list[str]
    entry_logic: str
    exit_logic: str

# LIST OF REAL INDICATORS (Grounding the Model)
SUPPORTED_INDICATORS = """
pandas_ta supported functions:
- df.ta.rsi(length=14, append=True) -> columns: ['RSI_14']
- df.ta.sma(length=50, append=True) -> columns: ['SMA_50']
- df.ta.ema(length=50, append=True) -> columns: ['EMA_50']
- df.ta.bbands(length=20, std=2, append=True) -> columns: ['BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']
- df.ta.macd(append=True) -> columns: ['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9']
- df.ta.atr(length=14, append=True) -> columns: ['ATRr_14']
- df.ta.adx(length=14, append=True) -> columns: ['ADX_14', 'DMP_14', 'DMN_14']
"""

def extract_strategy_from_images(images, max_retries=2):
    model = genai.GenerativeModel('gemini-2.5-flash') # Or 2.5-flash if available
    
    prompt = f"""
    Act as a Quantitative Python Developer. Extract the trading strategy.
    
    {SUPPORTED_INDICATORS}

    RULES:
    1. The input dataframe is ALWAYS named 'df'. DO NOT use 'data'.
    2. CALCULATE indicators using 'df.ta.indicator(..., append=True)'.
    3. COLUMNS are lowercase: df['close'], df['open'].
    4. DO NOT use loops or variables like 'previous_position'. 
       - WRONG: if previous_position == 1...
       - CORRECT: df['position'].shift(1)
    5. OUTPUT: Create a column 'entry_signal' (1=Buy, -1=Sell).
    
    OUTPUT JSON ONLY.
    """

    print("🤖 Sending to Gemini...")
    
    # 1. Initial Generation
    try:
        response = model.generate_content(
            [prompt] + images,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=StrategySchema
            )
        )
        data = json.loads(response.text)
    except Exception as e:
        print(f"❌ Initial Generation Failed: {e}")
        return None

    # 2. Refinement Loop (The "Self-Correction" Phase)
    for attempt in range(max_retries):
        is_valid, error_msg = LogicValidator.validate_strategy(data)
        
        if is_valid:
            print(f"✅ Strategy Logic Validated (Attempt {attempt+1})")
            return data
            
        print(f"⚠️ Validation Failed: {error_msg}. Retrying...")
        
        # Refinement Prompt
        refine_prompt = f"""
        The previous strategy extraction had Python Syntax Errors.
        ERROR: {error_msg}
        
        CURRENT JSON:
        {json.dumps(data)}
        
        Fix the 'entry_logic' or 'exit_logic' strings to be valid Python.
        """
        
        try:
            response = model.generate_content(
                refine_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=StrategySchema
                )
            )
            data = json.loads(response.text)
        except Exception as e:
            print(f"❌ Refinement Failed: {e}")
            break

    return data