# src/compression/processor_wop8.py
import os
import sys

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import STATS_DIR

from src.compression.wop8 import WOP8Compression
from src.reporting.spreadsheet import update_with_wop8_results

def apply_wop8_to_testing(run_name, test_paths, excel_path, best_weights):
    """
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
 # src/compression/processor_wop8.py
import os
import sys

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import STATS_DIR

from src.compression.wop8 import WOP8Compression
from src.reporting.spreadsheet import update_with_wop8_results

def apply_wop8_to_all_images(run_name, train_paths, test_paths, excel_path, best_weights):
    """
    Apply W-OP8 compression with best weights to ALL images and update spreadsheet.
    
    Args:
        dataset_name (str): Name of the dataset
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
    
    # Compress testing set (will be used to update the "Testing" sheet)
    print(f"Compressing {len(test_paths)} testing images...")
    test_results = wop8_compressor.compress_dataset(test_paths, run_name)
    
    # Compress training set (just for completeness, not updating the Training sheet)
    print(f"Compressing {len(train_paths)} training images...")
    train_results = wop8_compressor.compress_dataset(train_paths, run_name)
    
    # Combine all results
    all_results = {**train_results, **test_results}
    
    # Format results for spreadsheet update
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
    
    # Update spreadsheet
    print("Updating spreadsheet with W-OP8 results...")
    update_success = update_with_wop8_results(excel_path, formatted_results)
    
    # if update_success:
    #     print(f"Spreadsheet updated with W-OP8 results at: {excel_path}")
    # else:
    #     print("Failed to update spreadsheet with W-OP8 results")
    # After successfully updating the spreadsheet with W-OP8 results
    if update_success:
        # Import the summary sheet creation function
        from src.reporting.spreadsheet import create_summary_sheet
        
        # Create the summary sheet
        print("Creating summary sheet...")
        summary_success = create_summary_sheet(excel_path)
        
        if summary_success:
            print("Summary sheet created successfully!")
        else:
            print("Failed to create summary sheet")
        
        print(f"Spreadsheet updated with W-OP8 results at: {excel_path}")
    else:
        print("Failed to update spreadsheet with W-OP8 results")
    
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