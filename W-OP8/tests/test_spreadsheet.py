import os
import pandas as pd
import pytest
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reporting.spreadsheet import create_dataset_spreadsheet

def test_create_dataset_spreadsheet():
    # Create sample training and testing data
    train_stats = [
        {
            'image_name': 'train1.png',
            'width': 100,
            'height': 100,
            'num_pixels': 10000,
            'uncompressed_size_bytes': 30000,
            'baseline_size_bytes': 10000,
            'baseline_bpp': 8.0,
            'baseline_mae': 0.1
        },
        {
            'image_name': 'train2.png',
            'width': 200,
            'height': 200,
            'num_pixels': 40000,
            'uncompressed_size_bytes': 120000,
            'baseline_size_bytes': 40000,
            'baseline_bpp': 8.0,
            'baseline_mae': 0.2
        }
    ]
    
    test_stats = [
        {
            'image_name': 'test1.png',
            'width': 150,
            'height': 150,
            'num_pixels': 22500,
            'uncompressed_size_bytes': 67500,
            'baseline_size_bytes': 22500,
            'baseline_bpp': 8.0,
            'baseline_mae': 0.15
        }
    ]
    
    # Create spreadsheet
    run_name = "test_run"
    excel_path = create_dataset_spreadsheet(train_stats, test_stats, run_name)
    
    # Verify file exists
    assert os.path.exists(excel_path)
    
    # Read the Excel file
    train_df = pd.read_excel(excel_path, sheet_name='Training')
    test_df = pd.read_excel(excel_path, sheet_name='Testing')
    all_df = pd.read_excel(excel_path, sheet_name='All Images')
    
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
    assert len(test_df) == 2  # 1 image + 1 total row
    
    # Test all images sheet structure
    assert list(all_df.columns) == expected_test_columns
    assert len(all_df) == 4  # 3 images + 1 total row
    
    # Test totals row calculations in training sheet
    total_row = train_df[train_df['image_name'] == 'TOTAL'].iloc[0]
    assert total_row['num_pixels'] == 50000  # 10000 + 40000
    assert total_row['uncompressed_size_bytes'] == 150000  # 30000 + 120000
    assert total_row['baseline_size_bytes'] == 50000  # 10000 + 40000
    # BPP should be (50000 * 8) / 50000 = 8.0
    assert abs(total_row['baseline_bpp'] - 8.0) < 0.001
    # MAE should be average of 0.1 and 0.2
    assert abs(total_row['baseline_mae'] - 0.15) < 0.001
    
    # Test totals row calculations in testing sheet
    total_row = test_df[test_df['image_name'] == 'TOTAL'].iloc[0]
    assert total_row['num_pixels'] == 22500
    assert total_row['uncompressed_size_bytes'] == 67500
    assert total_row['baseline_size_bytes'] == 22500
    # BPP should be (22500 * 8) / 22500 = 8.0
    assert abs(total_row['baseline_bpp'] - 8.0) < 0.001
    assert abs(total_row['baseline_mae'] - 0.15) < 0.001
    
    # Test that WOP8 columns exist but are empty
    wop8_columns = ['wop8_size_bytes', 'wop8_bpp', 'wop8_mae',
                   'size_reduction_bytes', 'bpp_improvement',
                   'improvement_percentage']
    for col in wop8_columns:
        assert col in test_df.columns
        assert test_df[col].isna().all()
    
    # Clean up
    os.remove(excel_path)

def test_create_dataset_spreadsheet_empty_data():
    # Test with empty data
    train_stats = []
    test_stats = []
    run_name = "test_run_empty"
    
    excel_path = create_dataset_spreadsheet(train_stats, test_stats, run_name)
    
    # Verify file exists
    assert os.path.exists(excel_path)
    
    # Read the Excel file
    train_df = pd.read_excel(excel_path, sheet_name='Training')
    test_df = pd.read_excel(excel_path, sheet_name='Testing')
    
    # Test that sheets exist with correct columns but no data
    assert len(train_df) == 1  # Just the total row
    assert len(test_df) == 1  # Just the total row
    
    # Clean up
    os.remove(excel_path)

def test_create_dataset_spreadsheet_missing_data():
    # Test with missing data
    train_stats = [
        {
            'image_name': 'train1.png',
            'width': 100,
            'height': 100,
            'num_pixels': 10000,
            # Missing some fields
        }
    ]
    
    test_stats = [
        {
            'image_name': 'test1.png',
            'width': 150,
            'height': 150,
            'num_pixels': 22500,
            # Missing some fields
        }
    ]
    
    run_name = "test_run_missing"
    excel_path = create_dataset_spreadsheet(train_stats, test_stats, run_name)
    
    # Verify file exists
    assert os.path.exists(excel_path)
    
    # Read the Excel file
    train_df = pd.read_excel(excel_path, sheet_name='Training')
    test_df = pd.read_excel(excel_path, sheet_name='Testing')
    
    # Test that missing fields are filled with None
    assert train_df['baseline_size_bytes'].isna().all()
    assert train_df['baseline_bpp'].isna().all()
    assert train_df['baseline_mae'].isna().all()
    
    assert test_df['baseline_size_bytes'].isna().all()
    assert test_df['baseline_bpp'].isna().all()
    assert test_df['baseline_mae'].isna().all()
    
    # Clean up
    os.remove(excel_path) 