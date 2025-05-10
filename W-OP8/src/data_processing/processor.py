# src/data_processing/processor.py
import os
import sys
import argparse

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import INPUT_DIR, TRAIN_DIR, TEST_DIR

# Direct imports instead of relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_processing.validator import validate_directory
from src.data_processing.partitioner import partition_dataset
from src.data_processing.statistics import collect_statistics
from src.reporting.spreadsheet import create_dataset_spreadsheet
from src.compression.processor_wop8 import apply_wop8_to_testing

from src.compression.processor_wop8 import apply_wop8_to_all_images



# Import baseline compression functionality
from src.compression.baseline import BaselineCompression
from src.reporting.spreadsheet import update_spreadsheet_with_baseline

# Import GA optimization functionality
from src.genetic_algorithm.optimizer import optimize_weights

def get_first_dataset():
    """
    Get the first dataset directory in the input directory.
    
    Returns:
        str: Name of the first dataset directory, or None if no directories exist
    """
    try:
        for item in os.listdir(INPUT_DIR):
            item_path = os.path.join(INPUT_DIR, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                return item
    except Exception as e:
        print(f"Error finding datasets: {e}")
    return None

def process_dataset(dataset_name, train_ratio=0.1, seed=42, run_ga=True, ga_generations=24):
    """
    Process a dataset: validate, partition, collect statistics, create spreadsheets,
    run baseline compression, and optionally run GA optimization.
    
    Args:
        dataset_name (str): Name of the dataset directory in INPUT_DIR
        train_ratio (float): Ratio of images to use for training
        seed (int): Random seed for reproducibility
        run_ga (bool): Whether to run genetic algorithm optimization
        ga_generations (int): Number of generations for GA optimization
        
    Returns:
        dict: Processing results and statistics
    """
    # Setup paths
    dataset_dir = os.path.join(INPUT_DIR, dataset_name)
    train_dir = os.path.join(TRAIN_DIR, dataset_name)
    test_dir = os.path.join(TEST_DIR, dataset_name)
    
    print(f"Processing dataset '{dataset_name}'...")
    
    # Step 1: Validate PNG files
    print("Validating PNG files...")
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory '{dataset_dir}' does not exist")
        return {
            'status': 'error',
            'message': f"Dataset directory '{dataset_dir}' does not exist",
            'dataset': dataset_name
        }
    
    valid_files, invalid_files = validate_directory(dataset_dir)
    
    if not valid_files:
        print(f"Error: No valid PNG files found in {dataset_dir}")
        return {
            'status': 'error',
            'message': 'No valid PNG files found',
            'dataset': dataset_name
        }
    
    print(f"Found {len(valid_files)} valid PNG files")
    if invalid_files:
        print(f"Found {len(invalid_files)} invalid files (not PNG)")
        for file in invalid_files:
            print(f"  - {os.path.basename(file)}")
        # Throw error if there are invalid files
        raise ValueError("Invalid files found in dataset - Please ensure all files are PNG images")

    # Step 2: Partition dataset
    print("Partitioning dataset...")
    train_paths, test_paths = partition_dataset(
        valid_files, train_dir, test_dir, train_ratio, seed
    )
    
    print(f"Partitioned into {len(train_paths)} training and {len(test_paths)} testing files")
    
    # Step 3: Collect statistics
    print("Collecting statistics...")
    train_stats = collect_statistics(train_paths)
    test_stats = collect_statistics(test_paths)
    
    # Step 4: Create spreadsheet
    print("Creating spreadsheet...")
    excel_path = create_dataset_spreadsheet(train_stats, test_stats, dataset_name)
    
    # Step 5: Run baseline compression
    print("Setting up baseline compression...")
    compressor = BaselineCompression()
    
    if not compressor.setup(clean=True):
        return {
            'status': 'error',
            'message': 'Failed to set up baseline compression',
            'dataset': dataset_name
        }
    
    
    # Compress training set
    print("Compressing training set...")
    train_results = compressor.process_dataset(train_paths, dataset_name)
    
    # Compress testing set
    print("Compressing testing set...")
    test_results = compressor.process_dataset(test_paths, dataset_name)
    
    # Update spreadsheet with baseline results
    print("Updating spreadsheet with baseline results...")
    update_spreadsheet_with_baseline(excel_path, train_results, test_results)
     # Step 6: Run GA optimization (if requested)
    ga_results = None
    wop8_results = None
    
    if run_ga:
        print("\nRunning genetic algorithm optimization...")
        ga_results = optimize_weights(
            dataset_name=dataset_name,
            excel_path=excel_path,
            train_paths=train_paths,
            generations=ga_generations
        )
        
        # Store the best weights in results
        best_weights = ga_results['best_candidate']
        print(f"Optimization complete! Best weights: {best_weights}")
        
        # Step 7: Apply W-OP8 with best weights to all images
        wop8_results = apply_wop8_to_all_images(
            dataset_name=dataset_name,
            train_paths=train_paths,
            test_paths=test_paths,
            excel_path=excel_path,
            best_weights=best_weights
        )
        
        if wop8_results:
            print("\nW-OP8 compression complete!")
            
            # Calculate improvements on the testing set
            test_baseline_size = sum(result['size'] for name, result in test_results.items())
            test_wop8_size = sum(result['size'] for name, result in wop8_results['test_results'].items())
            test_improvement = test_baseline_size - test_wop8_size
            test_improvement_percent = (test_improvement / test_baseline_size) * 100
            
            print(f"\nResults on Testing Set ({len(test_paths)} images):")
            print(f"Baseline size: {test_baseline_size:,} bytes")
            print(f"W-OP8 size: {test_wop8_size:,} bytes")
            print(f"Size reduction: {test_improvement:,} bytes ({test_improvement_percent:.2f}%)")
            
            # Calculate overall improvements (all images)
            all_baseline_size = (
                sum(result['size'] for name, result in test_results.items()) + 
                sum(result['size'] for name, result in train_results.items())
            )
            all_wop8_size = sum(result['size'] for name, result in wop8_results['all_results'].items())
            all_improvement = all_baseline_size - all_wop8_size
            all_improvement_percent = (all_improvement / all_baseline_size) * 100
            
            print(f"\nResults on All Images ({len(train_paths) + len(test_paths)} images):")
            print(f"Baseline size: {all_baseline_size:,} bytes")
            print(f"W-OP8 size: {all_wop8_size:,} bytes")
            print(f"Size reduction: {all_improvement:,} bytes ({all_improvement_percent:.2f}%)")
        else:
            print("Failed to apply W-OP8 compression")
    
    print(f"Spreadsheet updated at: {excel_path}")
    
    # Return comprehensive results
    return {
        'status': 'success',
        'dataset': dataset_name,
        'valid_count': len(valid_files),
        'invalid_count': len(invalid_files),
        'train_count': len(train_paths),
        'test_count': len(test_paths),
        'train_paths': train_paths,
        'test_paths': test_paths,
        'excel_path': excel_path,
        'train_results': train_results,
        'test_results': test_results,
        'ga_results': ga_results,
        'wop8_results': wop8_results
    }

    

    
  

def main():
    """
    Main entry point when running as a script.
    """
    parser = argparse.ArgumentParser(description='Process an image dataset for W-OP8 compression testing')
    parser.add_argument('--dataset', help='Name of the dataset directory in the input folder')
    parser.add_argument('--train-ratio', type=float, default=0.1, 
                        help='Percentage of images to use for training (default: 0.1)')
    parser.add_argument('--seed', type=int, default=42, 
                        help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--skip-ga', action='store_true',
                        help='Skip genetic algorithm optimization')
    parser.add_argument('--ga-generations', type=int, default=3,
                        help='Number of generations for GA optimization (default: 24)')
    args = parser.parse_args()

    # If no dataset is specified, use the first one found
    dataset_name = args.dataset
    if not dataset_name:
        dataset_name = get_first_dataset()
        if dataset_name:
            print(f"No dataset specified, using first available: {dataset_name}")
        else:
            print("Error: No datasets found in input directory")
            sys.exit(1)

    result = process_dataset(
        dataset_name, 
        args.train_ratio, 
        args.seed,
        run_ga=not args.skip_ga,
        ga_generations=args.ga_generations
    )
    
    if result['status'] == 'success':
        print("\nProcessing completed successfully!")
        print(f"Dataset: {result['dataset']}")
        print(f"Valid PNG files: {result['valid_count']}")
        print(f"Training images: {result['train_count']}")
        print(f"Testing images: {result['test_count']}")
        print(f"Results spreadsheet: {result['excel_path']}")
        
        if result['ga_results']:
            print("\nGA Optimization Results:")
            print(f"Best weights: {result['ga_results']['best_candidate']}")
            print(f"Compression size: {-result['ga_results']['best_fitness']} bytes")
    else:
        print(f"\nError during processing: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()