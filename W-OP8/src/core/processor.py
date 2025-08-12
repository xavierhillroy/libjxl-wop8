# src/data_processing/processor.py
import os
import sys
import argparse

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import INPUT_DIR, TRAIN_DIR, TEST_DIR, generate_run_name

# Direct imports instead of relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_processing.validator import validate_directory
from src.data_processing.partitioner import partition_dataset
from src.data_processing.statistics import collect_statistics
from src.reporting.spreadsheet import create_dataset_spreadsheet

from src.compression.processor_wop8 import apply_wop8_to_all_images


# Import baseline compression functionality
from src.compression.baseline import BaselineCompression
from src.reporting.spreadsheet import update_spreadsheet_with_baseline, update_with_effort_results, create_summary_sheet

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


def process_dataset(dataset_name, train_ratio=0.1, max_train_images=10, seed=42, 
                   run_ga=True, ga_generations=24, population_size=30,
                   mutation_rate=0.05, crossover_rate=0.9, elitism_count=2, 
                   tournament_size=3, progress_callback=None):
    """
    Process a dataset: validate, partition, collect statistics, create spreadsheets,
    run baseline compression, and optionally run GA optimization.
    
    Args:
        dataset_name (str): Name of the dataset directory in INPUT_DIR
        train_ratio (float): Ratio of images to use for training
        max_train_images (int): Maximum number of training images
        seed (int): Random seed for reproducibility
        run_ga (bool): Whether to run genetic algorithm optimization
        ga_generations (int): Number of generations for GA optimization
        population_size (int): Size of GA population
        mutation_rate (float): GA mutation rate
        crossover_rate (float): GA crossover rate
        elitism_count (int): Number of elite individuals to preserve
        tournament_size (int): Tournament selection size
        progress_callback (callable): Optional callback for progress updates
            Signature: (phase, message, generation, best_weights, best_fitness, time_remaining)
        
    Returns:
        dict: Processing results and statistics
    """
    # Generate run name with all parameters
    run_name = generate_run_name(
        dataset_name=dataset_name,
        train_ratio=train_ratio,
        max_train_images=max_train_images,
        population_size=population_size,
        generations=ga_generations,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        elitism_count=elitism_count,
        tournament_size=tournament_size,
        seed=seed
    )
    
    # Setup paths - use run_name for outputs
    dataset_dir = os.path.join(INPUT_DIR, dataset_name)  # Still use dataset for input
    train_dir = os.path.join(TRAIN_DIR, run_name)        # Use run_name for outputs
    test_dir = os.path.join(TEST_DIR, run_name)
    
    print(f"Processing dataset '{dataset_name}' as run '{run_name}'...")
    
    # Step 1: Validate PNG files
    if progress_callback:
        progress_callback("setup", "Validating PNG files...")
    print("Validating PNG files...")
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory '{dataset_dir}' does not exist")
        return {
            'status': 'error',
            'message': f"Dataset directory '{dataset_dir}' does not exist",
            'dataset': dataset_name,
            'run_name': run_name
        }
    
    valid_files, invalid_files = validate_directory(dataset_dir)
    
    if not valid_files:
        print(f"Error: No valid PNG files found in {dataset_dir}")
        return {
            'status': 'error',
            'message': 'No valid PNG files found',
            'dataset': dataset_name,
            'run_name': run_name
        }
    
    print(f"Found {len(valid_files)} valid PNG files")
    if invalid_files:
        print(f"Found {len(invalid_files)} invalid files (not PNG)")
        for file in invalid_files:
            print(f"  - {os.path.basename(file)}")
        # Throw error if there are invalid files
        raise ValueError("Invalid files found in dataset - Please ensure all files are PNG images")

    # Step 2: Partition dataset
    if progress_callback:
        progress_callback("setup", "Partitioning dataset...")
    print("Partitioning dataset...")
    train_paths, test_paths = partition_dataset(
        valid_files, train_dir, test_dir, train_ratio, max_train_images, seed
    )
    print(f"Partitioned into {len(train_paths)} training and {len(test_paths)} testing files")
    
    # Step 3: Collect statistics
    print("Collecting statistics...")
    train_stats = collect_statistics(train_paths)
    test_stats = collect_statistics(test_paths)
    
    # Step 4: Create spreadsheet - use run_name
    print("Creating spreadsheet...")
    excel_path = create_dataset_spreadsheet(train_stats, test_stats, run_name)
    
    # Step 5: Run ALL baseline compressions at once
    if progress_callback:
        progress_callback("baseline", "Running baseline compression ...")
 
    print("Setting up baseline compression...")
    compressor = BaselineCompression()

    if not compressor.setup(clean=True):  # Compile original once
        return {'status': 'error', 'message': 'Failed to set up baseline compression'}

    # Compress training set (for GA comparison)
    print("Compressing training set with baseline...")
    train_results = compressor.process_dataset(train_paths, run_name)

    # Compress testing set (for final comparison)
    print("Compressing testing set with baseline...")
    test_results = compressor.process_dataset(test_paths, run_name)

    # # Compress ALL images at effort level 7 (no predictor mode)
    # print("Compressing all images with baseline effort 7...")
    # all_paths = train_paths + test_paths
    # baseline_effort7 = compressor.process_dataset_with_effort(all_paths, run_name, effort=7)

    # # Compress ALL images at effort level 9 (no predictor mode)
    # print("Compressing all images with baseline effort 9...")
    # baseline_effort9 = compressor.process_dataset_with_effort(all_paths, run_name, effort=9)

    # Update spreadsheet with ALL baseline results
    print("Updating spreadsheet with baseline results...")
    update_spreadsheet_with_baseline(excel_path, train_results, test_results)
    
    # Create summary sheet (with baseline results only initially)
    print("Creating summary sheet...")
    summary_success = create_summary_sheet(excel_path)
    if summary_success:
        print("Summary sheet created successfully")
    else:
        print("Failed to create summary sheet")
    # update_with_effort_results(excel_path, {
    #     'effort7': {'baseline': baseline_effort7, 'wop8': {}},
    #     'effort9': {'baseline': baseline_effort9, 'wop8': {}}
    # })
    
    # Step 6: Run GA optimization (if requested)
    ga_results = None
    wop8_results = None
    
    if run_ga:
        if progress_callback:
            progress_callback("ga", "Starting GA optimization...")
        print("\nRunning genetic algorithm optimization...")
        ga_results = optimize_weights(
            run_name=run_name,
            excel_path=excel_path,
            train_paths=train_paths,
            population_size=population_size,
            generations=ga_generations,
            mutation_rate=mutation_rate,
            crossover_rate=crossover_rate,
            elitism_count=elitism_count,
            tournament_size=tournament_size,
            progress_callback=progress_callback  # Pass through callback
        )
        
        # Store the best weights in results
        best_weights = ga_results['best_candidate']
        print(f"Optimization complete! Best weights: {best_weights}")
        
        # Step 7: Apply W-OP8 with best weights to all images
        if progress_callback:
            progress_callback("wop8", "Applying W-OP8 compression to all images...")
        wop8_results = apply_wop8_to_all_images(
            run_name=run_name,
            train_paths=train_paths,
            test_paths=test_paths,
            excel_path=excel_path,
            best_weights=best_weights
        )
        
        if wop8_results:
            print("\nW-OP8 compression complete!")
            print(f"Results saved to spreadsheet: {excel_path}")
        else:
            print("Failed to apply W-OP8 compression")
    
    print(f"Spreadsheet updated at: {excel_path}")
    
    # Return comprehensive results
    return {
        'status': 'success',
        'dataset': dataset_name,
        'run_name': run_name,  # Include run_name in results
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
    parser = argparse.ArgumentParser(
        description='Process an image dataset for W-OP8 compression testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process first available dataset with default settings
  python processor.py

  # Process specific dataset with custom training ratio
  python processor.py --dataset my_dataset --train-ratio 0.2

  # Run with custom GA parameters
  python processor.py --dataset my_dataset --population-size 50 --generations 30

  # Skip GA optimization
  python processor.py --dataset my_dataset --skip-ga

For more information about the W-OP8 compression algorithm and its parameters,
please refer to the documentation.
        """
    )
    
    # Essential arguments
    parser.add_argument('--dataset', 
        help='Name of the dataset directory in the input folder. If not specified, uses the first available dataset.')
    parser.add_argument('--train-ratio', type=float, default=0.1,
        help='Ratio of images to use for training (default: 0.1)')
    parser.add_argument('--max-train', type=int, default=10,
        help='Maximum number of training images to use (default: 10)')
    parser.add_argument('--seed', type=int, default=42,
        help='Random seed for reproducibility (default: 42)')
    
    # GA parameters
    ga_group = parser.add_argument_group('Genetic Algorithm Parameters')
    ga_group.add_argument('--population-size', type=int, default=30,
        help='Size of the GA population (default: 30)')
    ga_group.add_argument('--generations', type=int, default=24,
        help='Number of generations for GA optimization (default: 24)')
    ga_group.add_argument('--mutation-rate', type=float, default=0.05,
        help='Probability of mutation in GA (default: 0.05)')
    ga_group.add_argument('--crossover-rate', type=float, default=0.9,
        help='Probability of crossover in GA (default: 0.9)')
    ga_group.add_argument('--elitism-count', type=int, default=2,
        help='Number of elite individuals to preserve (default: 2)')
    ga_group.add_argument('--tournament-size', type=int, default=3,
        help='Size of tournament selection (default: 3)')
    
    # Control argument
    parser.add_argument('--skip-ga', action='store_true',
        help='Skip genetic algorithm optimization and only run baseline compression')

    # Parse arguments ONLY ONCE
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
    
    # Pass all parameters to process_dataset
    result = process_dataset(
        dataset_name=dataset_name,  # Use the processed dataset_name
        train_ratio=args.train_ratio,
        max_train_images=args.max_train,
        seed=args.seed,
        run_ga=not args.skip_ga,
        ga_generations=args.generations,  # Note: parameter name should match process_dataset
        population_size=args.population_size,
        mutation_rate=args.mutation_rate,
        crossover_rate=args.crossover_rate,
        elitism_count=args.elitism_count,
        tournament_size=args.tournament_size
    )
    
    if result['status'] == 'success':
        print("\nProcessing completed successfully!")
        print(f"Dataset: {result['dataset']}")
        print(f"Valid PNG files: {result['valid_count']}")
        print(f"Training images: {result['train_count']}")
        print(f"Testing images: {result['test_count']}")
        print(f"Results spreadsheet: {result['excel_path']}")
        
        if result.get('ga_results'):
            print("\nGA Optimization Results:")
            print(f"Best weights: {result['ga_results']['best_candidate']}")
            print(f"Compression size: {-result['ga_results']['best_fitness']} bytes")
    else:
        print(f"\nError during processing: {result['message']}")
        sys.exit(1)
if __name__ == "__main__":
    main()