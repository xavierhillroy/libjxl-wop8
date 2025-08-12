# src/compression/processor_wop8.py
import os
import sys

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import STATS_DIR
from config import CONTEXT_PREDICT_PATH, BUILD_DIR, COMPRESSED_DIR

from src.compression.wop8 import WOP8Compression
from src.reporting.spreadsheet import update_with_wop8_results, create_summary_sheet


def apply_wop8_to_testing(run_name, test_paths, excel_path, best_weights):
    """
    LEGACY FUNCTION
    Apply W-OP8 compression with best weights to the testing set and update spreadsheet.
    
    Args:
        dataset_name (str): Name of the dataset
        test_paths (list): List of paths to testing images
        excel_path (str): Path to Excel spreadsheet
        best_weights (list): List of 8 integer weights from GA optimization
        
    Returns:
        dict: Compression results
    """
    print(f"\nApplying W-OP8 compression to testing set with weights {best_weights}...")
    
    # Initialize W-OP8 compressor
    wop8_compressor = WOP8Compression()
    
    # Setup W-OP8 with best weights
    setup_success = wop8_compressor.setup_with_best_weights(best_weights)
    if not setup_success:
        print("Failed to set up W-OP8 with best weights")
        return None
    
    # Compress testing set
    print(f"Compressing {len(test_paths)} testing images...")
    wop8_results = wop8_compressor.compress_dataset(test_paths, run_name)
    
    # Format results for spreadsheet update
    formatted_results = {
        'results': [
            {
                'image_name': img_name,
                'size': result['size'],
                'mae': result['mae']
            }
            for img_name, result in wop8_results.items()
        ]
    }
    
    # Update spreadsheet
    print("Updating spreadsheet with W-OP8 results...")
    update_success = update_with_wop8_results(excel_path, formatted_results)
    
    if update_success:
        print(f"Spreadsheet updated with W-OP8 results at: {excel_path}")
        
        # Create summary sheet
        print("Creating summary sheet...")
        summary_success = create_summary_sheet(excel_path)
        if summary_success:
            print("Summary sheet created successfully")
        else:
            print("Failed to create summary sheet")
    else:
        print("Failed to update spreadsheet with W-OP8 results")
    
    # Save summary to stats file
    results_path = os.path.join(STATS_DIR, f"{run_name}_wop8_results.json")
    with open(results_path, 'w') as f:
        import json
        json.dump({
            'run_name': run_name,
            'best_weights': best_weights,
            'total_compressed_size': sum(result['size'] for result in wop8_results.values()),
            'average_mae': sum(result['mae'] for result in wop8_results.values()) / len(wop8_results) if wop8_results else 0,
            'compressed_count': len(wop8_results)
        }, f, indent=2)
    
    return wop8_results

def apply_different_effort_levels(run_name, all_paths, excel_path, best_weights):
    """
    Apply W-OP8 compression with different effort levels to all images and update spreadsheet.
    Note: Baseline compression is already done in the main processor.
    
    Args:
        run_name (str): Name of the run
        all_paths (list): List of paths to all images
        excel_path (str): Path to Excel spreadsheet
        best_weights (list): List of 8 integer weights from GA optimization
        
    Returns:
        dict: Compression results
    """
    print("\nRunning W-OP8 compression at different effort levels...")
    
    # Initialize W-OP8 compressor
    wop8_compressor = WOP8Compression()
    
    # Set up W-OP8 with best weights
    setup_success = wop8_compressor.setup_with_best_weights(best_weights)
    if not setup_success:
        print("Failed to set up W-OP8 with best weights for effort level comparisons")
        return None
    
    # Run W-OP8 compression at effort level 7
    print(f"Running W-OP8 compression with effort=7 on {len(all_paths)} images...")
    wop8_effort7 = wop8_compressor.compress_dataset_with_effort(all_paths, run_name, effort=7)
    
    # Run W-OP8 compression at effort level 9
    print(f"Running W-OP8 compression with effort=9 on {len(all_paths)} images...")
    wop8_effort9 = wop8_compressor.compress_dataset_with_effort(all_paths, run_name, effort=9)
    
    # Read existing baseline results from the effort level sheets
    from src.reporting.spreadsheet import update_with_effort_results
    
    # Update spreadsheet with W-OP8 results (baseline data is already there)
    print("Updating spreadsheet with W-OP8 effort level results...")
    
    # Read existing baseline data from sheets and combine with W-OP8 results
    import pandas as pd
    
    # Read existing effort level sheets
    effort7_df = pd.read_excel(excel_path, sheet_name='Effort Level 7')
    effort9_df = pd.read_excel(excel_path, sheet_name='Effort Level 9')
    
    # Extract baseline data from existing sheets
    baseline_effort7 = {}
    baseline_effort9 = {}
    
    for _, row in effort7_df.iterrows():
        if row['image_name'] != 'TOTAL' and 'baseline_size_bytes' in row and pd.notna(row['baseline_size_bytes']):
            baseline_effort7[row['image_name']] = {
                'size': row['baseline_size_bytes'],
                'mae': row['baseline_mae'] if 'baseline_mae' in row and pd.notna(row['baseline_mae']) else 0
            }
    
    for _, row in effort9_df.iterrows():
        if row['image_name'] != 'TOTAL' and 'baseline_size_bytes' in row and pd.notna(row['baseline_size_bytes']):
            baseline_effort9[row['image_name']] = {
                'size': row['baseline_size_bytes'],
                'mae': row['baseline_mae'] if 'baseline_mae' in row and pd.notna(row['baseline_mae']) else 0
            }
    
    update_with_effort_results(
        excel_path, 
        {
            'effort7': {
                'baseline': baseline_effort7,
                'wop8': wop8_effort7
            },
            'effort9': {
                'baseline': baseline_effort9,
                'wop8': wop8_effort9
            }
        }
    )
    
    # Store results
    effort_results = {
        'effort7': {
            'wop8': wop8_effort7
        },
        'effort9': {
            'wop8': wop8_effort9
        }
    }
    
    # Save results to stats file
    results_path = os.path.join(STATS_DIR, f"{run_name}_wop8_effort_results.json")
    with open(results_path, 'w') as f:
        import json
        json.dump({
            'run_name': run_name,
            'best_weights': best_weights,
            'effort7': {
                'wop8_total_size': sum(result['size'] for result in wop8_effort7.values()),
                'wop8_average_mae': sum(result['mae'] for result in wop8_effort7.values()) / len(wop8_effort7) if wop8_effort7 else 0
            },
            'effort9': {
                'wop8_total_size': sum(result['size'] for result in wop8_effort9.values()),
                'wop8_average_mae': sum(result['mae'] for result in wop8_effort9.values()) / len(wop8_effort9) if wop8_effort9 else 0
            }
        }, f, indent=2)
    
    return effort_results

def apply_wop8_to_all_images(run_name, train_paths, test_paths, excel_path, best_weights):
    """
    Apply W-OP8 compression with best weights to ALL images and update spreadsheet.
    Optimized to avoid redundant compression operations.
    
    Args:
        run_name (str): Name of the dataset
        train_paths (list): List of paths to training images
        test_paths (list): List of paths to testing images
        excel_path (str): Path to Excel spreadsheet
        best_weights (list): List of 8 integer weights from GA optimization
        
    Returns:
        dict: Compression results
    """
    all_paths = train_paths + test_paths
    print(f"\nApplying W-OP8 compression to all {len(all_paths)} images with weights {best_weights}...")
    
    # Initialize W-OP8 compressor
    wop8_compressor = WOP8Compression()
    
    # Setup W-OP8 with best weights
    setup_success = wop8_compressor.setup_with_best_weights(best_weights)
    if not setup_success:
        print("Failed to set up W-OP8 with best weights")
        return None
    
    # Step 1: Compress all images with predictor mode 6 (for Testing/All Images sheets)
    print(f"Compressing all {len(all_paths)} images with predictor mode 6...")
    all_results = wop8_compressor.compress_dataset(all_paths, run_name)
    
    # Separate results for testing and training
    test_results = {name: result for name, result in all_results.items() 
                   if any(test_path.endswith(name) for test_path in test_paths)}
    train_results = {name: result for name, result in all_results.items() 
                    if any(train_path.endswith(name) for train_path in train_paths)}
    
    # Format results for spreadsheet update (Testing and All Images sheets)
    formatted_results = {
        'results': [
            {
                'image_name': img_name,
                'size': result['size'],
                'mae': result['mae']
            }
            for img_name, result in all_results.items()
        ]
    }
    
    # Update Testing and All Images sheets
    print("Updating spreadsheet with W-OP8 results...")
    update_success = update_with_wop8_results(excel_path, formatted_results)
    
    if not update_success:
        print("Failed to update spreadsheet with W-OP8 results")
        return None
    
    # Create summary sheet
    print("Creating summary sheet...")
    summary_success = create_summary_sheet(excel_path)
    if summary_success:
        print("Summary sheet created successfully")
    else:
        print("Failed to create summary sheet")
    
    # # Step 2: Compress all images at different effort levels (for Effort Level sheets)
    # print("\nRunning effort level comparisons...")
    # effort_results = apply_different_effort_levels(run_name, all_paths, excel_path, best_weights)
    
    # if effort_results:
    #     print("Effort level comparisons completed and added to spreadsheet")
    # else:
    #     print("Failed to complete effort level comparisons")
    
    # print(f"Spreadsheet updated with W-OP8 results at: {excel_path}")
    
    # Save summary to stats file
    results_path = os.path.join(STATS_DIR, f"{run_name}_wop8_results.json")
    with open(results_path, 'w') as f:
        import json
        json.dump({
            'run_name': run_name,
            'best_weights': best_weights,
            'total_compressed_size': sum(result['size'] for result in all_results.values()),
            'average_mae': sum(result['mae'] for result in all_results.values()) / len(all_results) if all_results else 0,
            'compressed_count': len(all_results),
            'test_count': len(test_results),
            'train_count': len(train_results)
        }, f, indent=2)
    
    return {
        'all_results': all_results,
        'test_results': test_results,
        'train_results': train_results
    }