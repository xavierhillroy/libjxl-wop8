# W-OP8: Weight-Optimized JPEG XL Compression System

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Workflow Process](#workflow-process)
6. [File-by-File Documentation](#file-by-file-documentation)
7. [Output Files and Formats](#output-files-and-formats)
8. [Integration and Data Flow](#integration-and-data-flow)
9. [Installation and Setup](#installation-and-setup)
10. [Usage Guide](#usage-guide)
11. [API Reference](#api-reference)

## Overview

W-OP8 (Weight-Optimized 8-Predictor) is an automated system designed to optimize JPEG XL's lossless compression performance through genetic algorithm-enhanced predictor weights. The system extends JPEG XL's standard Weighted Average Predictor from 4 to 8 sub-predictors and uses evolutionary optimization to find optimal weight configurations for specific image datasets.

### Key Features
- Automated PNG dataset validation and partitioning
- Baseline JPEG XL compression benchmarking
- Genetic algorithm optimization of predictor weights
- W-OP8 enhanced compression implementation
- Comprehensive result tracking and analysis
- Text-based user interface for streamlined operation

## System Architecture

The W-OP8 system follows a modular architecture with the following major components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   Data Layer    │    │  Computation    │
│  (TUI/CLI)      │◄──►│  Management     │◄──►│    Layer        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                     │
         ▼                      ▼                     ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reporting     │    │   File System   │    │   JPEG XL       │
│    System       │◄──►│    Output       │◄──►│   Library       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Directory Structure

```
libjxl-wop8/
├── W-OP8/                           # Main W-OP8 Project Directory
│   ├── main.py                      # Application Entry Point
│   ├── config.py                    # Central Configuration Management
│   │
│   ├── data/                        # Data Processing Directory
│   │   ├── input/                   # User-provided PNG Image Datasets
│   │   ├── output/                  # System-generated Outputs
│   │   │   ├── compressed/          # Compressed Image Files
│   │   │   │   └── {run_name}/      # Per-experiment Organization
│   │   │   │       ├── baseline/    # Original JPEG XL Compression
│   │   │   │       ├── wop8/        # W-OP8 Optimized Compression  
│   │   │   │       ├── ga_candidates/ # Genetic Algorithm Training Images
│   │   │   │       ├── baseline_decompressed/
│   │   │   │       └── wop8_decompressed/
│   │   │   ├── spreadsheets/        # Excel Result Files
│   │   │   └── stats/               # JSON Statistical Data
│   │   ├── testing/                 # Test Set (90% of images)
│   │   └── training/                # Training Set (10% of images)
│   │
│   └── src/                         # Source Code Directory
│       ├── core/                    # Core Processing Logic
│       │   └── processor.py         # Main Workflow Controller
│       │
│       ├── compression/             # Compression Management
│       │   ├── baseline.py          # Standard JPEG XL Compression
│       │   ├── wop8.py              # W-OP8 Enhanced Compression
│       │   ├── processor_wop8.py    # W-OP8 Application Logic
│       │   └── context_manager.py   # Implementation Switcher
│       │
│       ├── data_processing/         # Data Handling Utilities
│       │   ├── validator.py         # PNG Format Validation
│       │   ├── partitioner.py       # Train/Test Set Creation
│       │   └── statistics.py        # Image Metadata Collection
│       │
│       ├── genetic_algorithm/       # Optimization Engine
│       │   ├── genetic_algorithm.py # Core GA Implementation
│       │   └── optimizer.py         # GA Wrapper Interface
│       │
│       ├── reporting/               # Results Management
│       │   └── spreadsheet.py       # Excel File Generation
│       │
│       └── tui/                     # Text User Interface
│           └── interface.py         # Interactive Console Interface
│
├── build/                          # JPEG XL Build Directory
├── lib/                           # JPEG XL Library Source
└── [additional JPEG XL directories]
```

## Core Components

### 1. Context Manager
The `context_manager.py` serves as the critical component that enables seamless switching between the original JPEG XL implementation and the W-OP8 enhanced version. It maintains separate versions of the `context_predict.h` file and handles library rebuilding.

### 2. Genetic Algorithm Engine
The `genetic_algorithm.py` implements a complete evolutionary optimization system that:
- Evaluates predictor weight configurations through actual compression
- Maintains a population of candidate solutions
- Uses tournament selection, uniform crossover, and mutation
- Caches evaluations for efficiency

### 3. Compression Processors
- **Baseline**: Handles standard JPEG XL compression for benchmarking
- **W-OP8**: Applies optimized weights for enhanced compression
- **Processor**: Orchestrates the application of W-OP8 to entire datasets

### 4. Data Management
- **Validator**: Ensures input data quality (PNG format validation)
- **Partitioner**: Creates reproducible train/test splits
- **Statistics**: Collects image metadata and compression metrics

### 5. Reporting System
Comprehensive Excel-based reporting with multiple sheets:
- Training data with GA candidate evaluations
- Testing results comparing baseline and W-OP8
- All images combined metrics
- Executive summary with key performance indicators

## Workflow Process

```
1. Data Validation
   ├── PNG format verification
   └── Invalid file identification

2. Dataset Partitioning
   ├── Random 10/90 split (training/testing)
   └── Seed-controlled reproducibility

3. Baseline Compression
   ├── Switch to original JPEG XL
   ├── Compress all images
   └── Calculate baseline metrics

4. Genetic Algorithm Optimization
   ├── Initialize population of weight configurations
   ├── Evaluate candidates by compression
   ├── Evolve through multiple generations
   └── Identify optimal weights

5. W-OP8 Application
   ├── Apply optimized weights
   ├── Compress all images
   └── Calculate improvement metrics

6. Results Generation
   ├── Update Excel spreadsheets
   ├── Generate summary statistics
   └── Create final reports
```

## File-by-File Documentation

### Core Configuration

#### `config.py`
**Purpose**: Central configuration hub for the entire system
**Key Functions**:
- `generate_run_name()`: Creates standardized run names with all parameters
- Directory path management
- Automatic directory creation

**Important Variables**:
```python
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
CONTEXT_PREDICT_PATH = os.path.join(LIB_DIR, 'jxl', 'modular', 'encoding', 'context_predict.h')
```

#### `main.py`
**Purpose**: Application entry point
**Key Functions**:

- Initializes TUI interface
- Handles global exception handling

### Compression Management

#### `context_manager.py`
**Purpose**: Critical manager for switching between JPEG XL implementations
**Key Functions**:
- `ensure_versions_exist()`: Validates presence of implementation files
- `use_original()`: Switches to baseline JPEG XL
- `use_wop8()`: Switches to W-OP8 implementation
- `update_wop8_weights()`: Updates predictor weights programmatically
- `rebuild_library()`: Rebuilds JPEG XL after source modifications

**Critical Files Managed**:
- `context_predict_original.h`: Backup of original implementation
- `context_predict_wop8.h`: Backup of W-OP8 implementation
- `context_predict.h`: Active implementation file

#### `baseline.py`
**Purpose**: Handles standard JPEG XL compression
**Key Functions**:
- `setup()`: Prepares baseline compression environment
- `compress_image()`: Compresses individual images
- `process_dataset()`: Batch processes image collections
- `calculate_mae()`: Computes Mean Absolute Error for verification

**Output Structure**:
```
{run_name}/baseline/
├── {image_name}.jxl           # Compressed files
└── baseline_decompressed/     # Verification files
    └── {image_name}.png
```

#### `wop8.py`
**Purpose**: Implements W-OP8 enhanced compression
**Key Functions**:
- `setup_with_best_weights()`: Configures optimized weights
- `compress_dataset()`: Applies W-OP8 to image collections

**Dependencies**: Reuses `BaselineCompression` infrastructure

#### `processor_wop8.py`
**Purpose**: Orchestrates W-OP8 application to datasets
**Key Functions**:
- `apply_wop8_to_testing()`: Processes test set with optimal weights
- `apply_wop8_to_all_images()`: Processes complete dataset
- Integrates with spreadsheet reporting

### Data Processing

#### `validator.py`
**Purpose**: Ensures data quality and format compliance
**Key Functions**:
- `is_png()`: Validates individual file format
- `validate_directory()`: Batch validates image directories

**Output**: Lists of valid/invalid file paths

#### `partitioner.py`
**Purpose**: Creates reproducible train/test splits
**Key Functions**:
- `partition_dataset()`: Random partitioning with seed control
- Supports customizable train ratio and maximum training images

**Parameters**:
- `train_ratio`: Default 0.1 (10% training)
- `max_train_images`: Default 10 images
- `seed`: Reproducibility control

#### `statistics.py`
**Purpose**: Collects image metadata
**Key Functions**:
- `get_image_statistics()`: Extracts individual image properties
- `collect_statistics()`: Batch processes multiple images

**Collected Metrics**:
- Image dimensions
- Pixel count
- Uncompressed size calculations
- Format information

### Genetic Algorithm Implementation

#### `genetic_algorithm.py`
**Purpose**: Core evolutionary optimization engine
**Key Components**:

1. **Population Management**:
   - Population size: 30 candidates (default)
   - Generations: 24 (default)
   - Weight range: 0-15 for each of 8 predictors

2. **Genetic Operators**:
   - Tournament selection (size: 3)
   - Uniform crossover (rate: 0.9)
   - Mutation (rate: 0.05)
   - Elitism (count: 2)

3. **Evaluation System**:
   - Fitness = -compressed_size (lower is better)
   - Evaluation caching for efficiency
   - Progress tracking with time estimation

**Key Functions**:
- `_evaluate_candidate()`: Tests weight configurations
- `run()`: Executes complete optimization process
- `update_spreadsheet()`: Records GA progress

#### `optimizer.py`
**Purpose**: High-level GA interface
**Key Functions**:
- Wraps GA implementation
- Manages parameter configuration
- Facilitates integration with main workflow

### Reporting System

#### `spreadsheet.py`
**Purpose**: Comprehensive Excel-based reporting (most complex file)
**Key Functions**:

1. **Multi-sheet Creation**:
   - `create_dataset_spreadsheet()`: Initializes workbook structure
   - Training, Testing, All Images, and Summary sheets

2. **Dynamic Updates**:
   - `update_spreadsheet_with_ga_candidate()`: Records GA evaluations
   - `update_spreadsheet_with_baseline()`: Adds baseline metrics
   - `update_with_wop8_results()`: Incorporates W-OP8 results

3. **Calculated Metrics**:
   - Bits per pixel (bpp)
   - Compression ratios
   - Improvement percentages
   - Size reductions

**Spreadsheet Structure**:
```
Training Sheet:
- Image metadata
- Baseline compression results
- GA candidate evaluations (w{weights}_fitness, w{weights}_mae)

Testing Sheet:
- Image metadata
- Baseline vs W-OP8 comparison
- Derived metrics (improvements, ratios)

All Images Sheet:
- Combined dataset results
- Aggregate statistics

Summary Sheet:
- Executive summary
- Key performance indicators
- Total improvements
```

### User Interface

#### `interface.py`
**Purpose**: Text-based user interface
**Key Components**:

1. **Screen Management**:
   - Main menu
   - Quick settings
   - Detailed GA parameters
   - Live progress display
   - Results presentation

2. **Progress Tracking**:
   - Real-time GA status
   - Time remaining estimates
   - Current best weights display

3. **User Input**:
   - Dataset selection
   - Parameter configuration
   - Run confirmation

**Key Features**:
- Rich console formatting
- Live updates during GA execution
- Path formatting for user-friendly display

### Core Orchestration

#### `processor.py`
**Purpose**: Main workflow controller
**Key Functions**:
- `process_dataset()`: Orchestrates complete workflow
- `main()`: CLI interface implementation
- Progress callback integration for TUI

**Workflow Steps**:
1. Data validation
2. Dataset partitioning
3. Baseline compression
4. GA optimization
5. W-OP8 application
6. Results generation

**CLI Parameters**:
- Dataset selection
- Training ratio
- Maximum training images
- Random seed
- All GA parameters
- Option to skip GA optimization

## Output Files and Formats

### Run Naming Convention
All outputs use a standardized naming pattern:
```
{dataset}_tr{train_ratio}_max{max_train}_p{pop_size}_g{generations}_m{mutation_rate}_x{crossover_rate}_e{elitism}_t{tournament}
```

Example: `Kodak_tr0.1_max10_p30_g24_m0.05_x0.9_e2_t3`

### Output Categories

#### 1. Compressed Images
```
data/output/compressed/{run_name}/
├── baseline/
│   ├── {image}.jxl
│   └── baseline_decompressed/{image}.png
├── wop8/
│   ├── {image}.jxl
│   └── wop8_decompressed/{image}.png
└── ga_candidates/
    └── w{weights}/
        ├── {image}.jxl
        └── dec_{image}.png
```

#### 2. Excel Spreadsheets
**File**: `{run_name}_results.xlsx`
- Training sheet with GA evaluations
- Testing sheet with comparisons
- All Images combined results
- Summary sheet with executive metrics

#### 3. Statistical Data
```
data/output/stats/
├── {run_name}_ga_results.json
├── {run_name}_best_weights.json
└── {run_name}_wop8_results.json
```

### Data Formats

#### JSON Statistics
```json
{
  "run_name": "dataset_tr0.1_max10_p30_g24_m0.05_x0.9_e2_t3",
  "best_weights": [1, 0, 1, 8, 15, 0, 15, 12],
  "best_fitness": -125486.0,
  "total_size": 125486,
  "generation_results": [...]
}
```

#### Excel Sheet Columns
**Training Sheet**:
- image_name, width, height, num_pixels
- uncompressed_size_bytes, baseline_size_bytes, baseline_bpp, baseline_mae
- w{weights}_fitness, w{weights}_mae (for each GA candidate)

**Testing Sheet**:
- All training columns plus:
- wop8_size_bytes, wop8_bpp, wop8_mae
- size_reduction_bytes, bpp_improvement, improvement_percentage

## Integration and Data Flow

### Component Integration Flow

```
1. Entry Point (main.py)
   ↓
2. User Interface (interface.py)
   ↓ [User Configuration]
3. Core Processor (processor.py)
   ↓ [Workflow Orchestration]
4. Data Validation (validator.py)
   ↓ [PNG Verification]
5. Data Partitioning (partitioner.py)
   ↓ [Train/Test Split]
6. Statistics Collection (statistics.py)
   ↓ [Image Metadata]
7. Spreadsheet Initialization (spreadsheet.py)
   ↓ [Excel Setup]
8. Baseline Compression
   ├── Context Manager → Original JPEG XL
   ├── Baseline Compression → Image Processing
   └── Spreadsheet Update → Results Recording
   ↓
9. GA Optimization
   ├── Genetic Algorithm → Weight Evolution
   ├── Context Manager → W-OP8 Switching
   ├── Compression Evaluation → Fitness Calculation
   └── Spreadsheet Update → Progress Tracking
   ↓
10. W-OP8 Application
    ├── Context Manager → Final Weight Application
    ├── W-OP8 Compression → Optimized Processing
    └── Final Results → Complete Analysis
    ↓
11. Results Presentation
    ├── Spreadsheet Summary → Excel Reports
    ├── JSON Statistics → Raw Data Export
    └── TUI Display → User Feedback
```

### Data Flow Between Components

```
Input Images → Validator → Partitioner → Statistics
                                             ↓
     Baseline Compression ← Context Manager → Spreadsheet
           ↓                                      ↑
     GA Evaluation → Genetic Algorithm → Optimizer
           ↓                                      ↑
     W-OP8 Compression ← Context Manager → Final Results
```

### Critical Integration Points

1. **Context Manager**: Central hub for implementation switching
2. **Spreadsheet System**: Persistent data store throughout workflow
3. **Progress Callbacks**: Real-time communication between processor and TUI
4. **Run Naming**: Consistent identification across all outputs
5. **Parameter Passing**: Standardized configuration through all components

## Installation and Setup

### Prerequisites
- Linux/macOS environment
- Python 3.8+
- JPEG XL library with build tools
- Ninja build system

### Required Python Packages
```
pandas
openpyxl
PIL (Pillow)
numpy
rich
pyfiglet
tqdm
```

### Installation Steps
1. Clone the libjxl-wop8 repository
2. Navigate to the W-OP8 directory
3. Install Python dependencies
4. Build JPEG XL library using provided build scripts
5. Place PNG datasets in `data/input/{dataset_name}/`

## Usage Guide

### Quick Start
```bash
cd W-OP8
python main.py
```

### CLI Usage
```bash
# Process with default settings
python processor.py --dataset my_dataset

# Custom training ratio and GA parameters
python processor.py --dataset my_dataset --train-ratio 0.15 --population-size 50 --generations 30

# Skip GA optimization
python processor.py --dataset my_dataset --skip-ga
```

### TUI Navigation
1. **Main Menu**: Start new analysis, view instructions, or check results
2. **Quick Settings**: Basic configuration (dataset, training ratio)
3. **Detailed Settings**: Advanced GA parameter customization
4. **Progress Screen**: Real-time optimization monitoring
5. **Results View**: Comprehensive output summary

## API Reference

### Core Functions

#### `process_dataset()`
```python
def process_dataset(dataset_name, train_ratio=0.1, max_train_images=10, 
                   seed=42, run_ga=True, ga_generations=24, 
                   population_size=30, mutation_rate=0.05, 
                   crossover_rate=0.9, elitism_count=2, 
                   tournament_size=3, progress_callback=None)
```
Main workflow controller that orchestrates the complete W-OP8 pipeline.

#### `generate_run_name()`
```python
def generate_run_name(dataset_name, train_ratio, max_train_images, 
                     population_size, generations, mutation_rate, 
                     crossover_rate, elitism_count, tournament_size)
```
Generates standardized run identifiers including all parameters.

### Key Classes

#### `GeneticAlgorithm`
```python
class GeneticAlgorithm:
    def __init__(self, run_name, excel_path, train_paths, ...):
    def run(self, progress_callback=None):
    def _evaluate_candidate(self, candidate):
```

#### `ContextFileManager`
```python
class ContextFileManager:
    def ensure_versions_exist(self):
    def use_original(self):
    def use_wop8(self):
    def update_wop8_weights(self, weights):
    def rebuild_library(self, clean=False):
```

#### `WOP8Interface`
```python
class WOP8Interface:
    def run(self):
    def show_main_menu(self):
    def show_running_screen(self):
    def show_results(self):
```



