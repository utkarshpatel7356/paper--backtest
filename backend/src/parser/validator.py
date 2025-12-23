import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CodeValidator")

class LogicValidator:
    """
    Checks if the extracted strategy logic strings are valid Python syntax.
    """
    
    @staticmethod
    def is_valid_python(code_str: str) -> tuple[bool, str]:
        """
        Returns (True, "") if valid.
        Returns (False, error_message) if invalid.
        """
        if not code_str or code_str == "False":
            return True, ""

        try:
            # Wrap in a function to ensure it parses as valid execution logic
            # We mock 'df' and 'ta' availability
            wrapped_code = f"def logic(df, np, ta):\n    {code_str}"
            ast.parse(wrapped_code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax Error: {e.msg} at line {e.lineno}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def validate_strategy(data: dict) -> tuple[bool, str]:
        """
        Validates the entry_logic and exit_logic fields of the JSON strategy.
        """
        # 1. Check Entry Logic
        is_valid, err = LogicValidator.is_valid_python(data.get('entry_logic', ''))
        if not is_valid:
            return False, f"Entry Logic Error: {err}"

        # 2. Check Exit Logic
        is_valid, err = LogicValidator.is_valid_python(data.get('exit_logic', ''))
        if not is_valid:
            return False, f"Exit Logic Error: {err}"

        return True, "Valid"