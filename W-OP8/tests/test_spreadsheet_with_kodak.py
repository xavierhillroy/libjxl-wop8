import os
import sys
import pytest
import pandas as pd

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.processor import process_dataset
from src.reporting.spreadsheet import create_dataset_spreadsheet

def test_create_dataset_spreadsheet_with_kodak():
    """
    Test spreadsheet creation using actual Kodak dataset processing.
    This test will:
    1. Process the Kodak dataset up to spreadsheet creation
    2. Verify the spreadsheet structure and calculations
    3. Clean up test files
    """
    # Process Kodak dataset with minimal settings
    result = process_dataset(
        dataset_name='kodak',
        train_ratio=0.1,  # Use 10% for training
        max_train_images=2,  # Limit to 2 training images
        seed=42,
        run_ga=False  # Skip GA optimization
    )
    
    # Verify processing was successful
    assert result['status'] == 'success'
    assert os.path.exists(result['excel_path'])
    
    # Read the Excel file
    train_df = pd.read_excel(result['excel_path'], sheet_name='Training')
    test_df = pd.read_excel(result['excel_path'], sheet_name='Testing')
    all_df = pd.read_excel(result['excel_path'], sheet_name='All Images')
    
    # Test training sheet structure
    expected_train_columns = [
        'image_name', 'width', 'height', 'num_pixels',
        'uncompressed_size_bytes', 'baseline_size_bytes',
        'baseline_bpp', 'baseline_mae'
    ]
    assert list(train_df.columns) == expected_train_columns
    assert len(train_df) == 3  # 2 images + 1 total row
    
    # Test testing sheet structure
    expected_test_columns = [
        'image_name', 'width', 'height', 'num_pixels',
        'uncompressed_size_bytes', 'baseline_size_bytes',
        'baseline_bpp', 'baseline_mae',
        'wop8_size_bytes', 'wop8_bpp', 'wop8_mae',
        'size_reduction_bytes', 'bpp_improvement',
        'improvement_percentage'
    ]
    assert list(test_df.columns) == expected_test_columns
    assert len(test_df) > 1  # At least 1 image + 1 total row
    
    # Test all images sheet structure
    assert list(all_df.columns) == expected_test_columns
    assert len(all_df) > 2  # At least 2 images + 1 total row
    
    # Test totals row calculations in training sheet
    total_row = train_df[train_df['image_name'] == 'TOTAL'].iloc[0]
    assert total_row['num_pixels'] > 0
    assert total_row['uncompressed_size_bytes'] > 0
    assert total_row['baseline_size_bytes'] > 0
    assert total_row['baseline_bpp'] > 0
    assert total_row['baseline_mae'] > 0
    
    # Test totals row calculations in testing sheet
    total_row = test_df[test_df['image_name'] == 'TOTAL'].iloc[0]
    assert total_row['num_pixels'] > 0
    assert total_row['uncompressed_size_bytes'] > 0
    assert total_row['baseline_size_bytes'] > 0
    assert total_row['baseline_bpp'] > 0
    assert total_row['baseline_mae'] > 0
    
    # Test that WOP8 columns exist but are empty
    wop8_columns = ['wop8_size_bytes', 'wop8_bpp', 'wop8_mae',
                   'size_reduction_bytes', 'bpp_improvement',
                   'improvement_percentage']
    for col in wop8_columns:
        assert col in test_df.columns
        assert test_df[col].isna().all()
    
    # Clean up
    os.remove(result['excel_path']) 