# W-OP8/config.py
import os
from datetime import datetime

# Determine the project root (libjxl-wop8/)
# Since this file is in W-OP8/, we need to go up one level
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# W-OP8 specific paths
WOP8_DIR = os.path.join(PROJECT_ROOT, 'W-OP8')
DATA_DIR = os.path.join(WOP8_DIR, 'data')

# Data directory structure
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
TRAIN_DIR = os.path.join(DATA_DIR, 'training')
TEST_DIR = os.path.join(DATA_DIR, 'testing')

# Output subdirectories
COMPRESSED_DIR = os.path.join(OUTPUT_DIR, 'compressed')
SPREADSHEETS_DIR = os.path.join(OUTPUT_DIR, 'spreadsheets')
STATS_DIR = os.path.join(OUTPUT_DIR, 'stats')

# Core JPEG XL library paths
LIB_DIR = os.path.join(PROJECT_ROOT, 'lib')
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')

# Important file paths
CONTEXT_PREDICT_PATH = os.path.join(LIB_DIR, 'jxl', 'modular', 'encoding', 'context_predict.h')
# Add to config.py
def generate_run_name(dataset_name, train_ratio, max_train_images, 
                     population_size, generations, mutation_rate, 
                     crossover_rate, elitism_count, tournament_size):
    """
    Generate a standardized run name including all parameters and datetime.
    
    Returns:
        str: Formatted name including all parameters and datetime
    """
    # Get current datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Format numbers nicely
    train_ratio_str = f"{train_ratio:.2f}".rstrip('0').rstrip('.')
    mutation_rate_str = f"{mutation_rate:.3f}".rstrip('0').rstrip('.')
    crossover_rate_str = f"{crossover_rate:.2f}".rstrip('0').rstrip('.')
    
    return (f"{dataset_name}_tr{train_ratio_str}_max{max_train_images}_"
            f"p{population_size}_g{generations}_m{mutation_rate_str}_"
            f"x{crossover_rate_str}_e{elitism_count}_t{tournament_size}_"
            f"{timestamp}")

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, TRAIN_DIR, TEST_DIR, 
                 COMPRESSED_DIR, SPREADSHEETS_DIR, STATS_DIR]:
    os.makedirs(directory, exist_ok=True)