import os
import argparse
from src.parser.pdf_processor import convert_pdf_to_images
from src.parser.gemini_client import extract_strategy_from_images
from src.parser.generator import save_strategy_file

def main():
    # 1. Setup Arguments
    parser = argparse.ArgumentParser(description="Alpha-Mechanism Phase 1: Scholar Parser")
    parser.add_argument("pdf_name", help="Name of the PDF file in data/input_papers")
    args = parser.parse_args()

    # 2. Define Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "data", "input_papers", args.pdf_name)

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    # 3. Pipeline Execution
    print("--- 🚀 Starting Alpha-Mechanism Parser ---")
    
    # Step A: PDF -> Images
    images = convert_pdf_to_images(pdf_path)
    if not images: return

    # Step B: Images -> JSON (Gemini)
    strategy_data = extract_strategy_from_images(images)
    if not strategy_data: return

    print(f"💡 Extracted Strategy: {strategy_data['strategy_name']}")

    # Step C: JSON -> Python File
    save_strategy_file(strategy_data)

    print("--- 🏁 Phase 1 Complete ---")

if __name__ == "__main__":
    main()