# W-OP8/config.py
import os

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

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, TRAIN_DIR, TEST_DIR, 
                 COMPRESSED_DIR, SPREADSHEETS_DIR, STATS_DIR]:
    os.makedirs(directory, exist_ok=True)