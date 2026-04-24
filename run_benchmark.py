import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.memory_agent.benchmark import BenchmarkSuite

# Setup logging
os.makedirs("logs", exist_ok=True)
log_file = f"logs/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BenchmarkRunner")

def main():
    load_dotenv()
    if not os.getenv("NVIDIA_API_KEY"):
        print("Error: NVIDIA_API_KEY not found in environment.")
        # We'll allow it to continue if the user provides it manually, 
        # but for this automation, I'll stop here or provide a placeholder.
        # Actually, I'll just print a warning.
        
    suite = BenchmarkSuite()
    logger.info("Starting Benchmark...")
    results = suite.run_benchmark()
    logger.info("Generating Reports...")
    suite.generate_report(results)
    logger.info(f"Done! Check report.md, BENCHMARK.md and {log_file}")

if __name__ == "__main__":
    main()
