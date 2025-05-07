# src/reporting/spreadsheet.py
import os
import sys
import pandas as pd

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import SPREADSHEETS_DIR

def create_dataset_spreadsheet(train_stats, test_stats, dataset_name):
    """
    Create a spreadsheet with multiple sheets for a dataset.
    
    Args:
        train_stats (list): List of dictionaries with training image statistics
        test_stats (list): List of dictionaries with testing image statistics
        dataset_name (str): Name of the dataset
    
    Returns:
        str: Path to the created spreadsheet
    """
    # Create directory if it doesn't exist
    os.makedirs(SPREADSHEETS_DIR, exist_ok=True)
    excel_path = os.path.join(SPREADSHEETS_DIR, f"{dataset_name}_results.xlsx")
    
    # Define columns for training sheet
    train_columns = [
        'image_name',
        'width',
        'height',
        'num_pixels',
        'uncompressed_size_bytes',
        'baseline_size_bytes',
        'baseline_bpp',
        'baseline_mae'
    ]
    
    # Define columns for testing sheet
    test_columns = [
        'image_name',
        'width',
        'height',
        'num_pixels',
        'uncompressed_size_bytes',
        'baseline_size_bytes',
        'baseline_bpp',
        'baseline_mae',
        'wop8_size_bytes',
        'wop8_bpp',
        'wop8_mae',
        'size_reduction_bytes',
        'bpp_improvement',
        'improvement_percentage'
    ]
    
    # Create training DataFrame and ensure all columns exist
    train_df = pd.DataFrame(train_stats)
    for col in train_columns:
        if col not in train_df.columns:
            train_df[col] = None
    
    # Ensure columns are in the right order
    train_df = train_df[train_columns]
    
    # Create testing DataFrame and ensure all columns exist
    test_df = pd.DataFrame(test_stats)
    for col in test_columns:
        if col not in test_df.columns:
            test_df[col] = None
    
    # Ensure columns are in the right order
    test_df = test_df[test_columns]
    
    # Create all images DataFrame with the same structure as testing
    all_stats = train_stats + test_stats
    all_df = pd.DataFrame(all_stats)
    for col in test_columns:
        if col not in all_df.columns:
            all_df[col] = None
    
    # Ensure columns are in the right order
    all_df = all_df[test_columns]
    
    # Write to Excel file with multiple sheets
    with pd.ExcelWriter(excel_path) as writer:
        train_df.to_excel(writer, sheet_name='Training', index=False)
        test_df.to_excel(writer, sheet_name='Testing', index=False)
        all_df.to_excel(writer, sheet_name='All Images', index=False)
        
        # Add a totals row to each sheet
        for sheet_name in ['Training', 'Testing', 'All Images']:
            worksheet = writer.sheets[sheet_name]
            num_rows = len(train_df) if sheet_name == 'Training' else (len(test_df) if sheet_name == 'Testing' else len(all_df))
            worksheet.cell(row=num_rows+2, column=1, value="TOTAL")
            
            # Add SUM formulas for size columns (bytes) and pixel columns
            size_columns = ['E', 'F', 'I', 'L']  # uncompressed_size_bytes, baseline_size_bytes, wop8_size_bytes, size_reduction_bytes
            pixel_columns = ['D']  # num_pixels
            
            # Calculate sums for both size and pixel columns
            for col in pixel_columns + size_columns:
                # Skip WOP8 columns in training sheet
                if (col in ['I', 'L']) and sheet_name == 'Training':
                    continue
                
                column_index = ord(col) - ord('A') + 1
                columns_in_sheet = len(train_columns) if sheet_name == 'Training' else len(test_columns)
                
                if column_index <= columns_in_sheet:
                    formula = f"=SUM({col}2:{col}{num_rows+1})"
                    worksheet.cell(row=num_rows+2, column=column_index, value=formula)
            
            # Add AVERAGE formulas for bpp columns
            bpp_columns = ['G', 'J', 'M']  # baseline_bpp, wop8_bpp, bpp_improvement
            for col in bpp_columns:
                if (col in ['J', 'M']) and sheet_name == 'Training':
                    continue
                
                column_index = ord(col) - ord('A') + 1
                columns_in_sheet = len(train_columns) if sheet_name == 'Training' else len(test_columns)
                
                if column_index <= columns_in_sheet:
                    formula = f"=AVERAGE({col}2:{col}{num_rows+1})"
                    worksheet.cell(row=num_rows+2, column=column_index, value=formula)
                
            # Add AVERAGE formula for improvement percentage
            if sheet_name != 'Training':
                improvement_col = 'N'  # Column for improvement_percentage
                column_index = ord(improvement_col) - ord('A') + 1
                
                if column_index <= len(test_columns):
                    formula = f"=AVERAGE({improvement_col}2:{improvement_col}{num_rows+1})"
                    worksheet.cell(row=num_rows+2, column=column_index, value=formula)
    
    return excel_path

def update_training_sheet_with_ga_results(excel_path, ga_results):
    """
    Update the training sheet with GA results.
    
    Args:
        excel_path (str): Path to the Excel file
        ga_results (dict): Dictionary with GA results
            {
                'weight_configs': [
                    {
                        'weights': [1, 5, 3, 7, 2, 0, 4, 1],
                        'results': [
                            {'image_name': 'img1.png', 'size': 1000, 'mae': 0.0},
                            ...
                        ]
                    },
                    ...
                ]
            }
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing Excel file
        train_df = pd.read_excel(excel_path, sheet_name='Training')
        
        # For each weight configuration
        for config in ga_results['weight_configs']:
            weights = config['weights']
            weight_str = '_'.join(map(str, weights))
            column_prefix = f"w{weight_str}"
            
            # Add columns for this weight configuration
            train_df[f"{column_prefix}_size_bytes"] = None
            train_df[f"{column_prefix}_bpp"] = None
            train_df[f"{column_prefix}_mae"] = None
            train_df[f"{column_prefix}_fitness"] = None
            
            # Fill data for each image
            for result in config['results']:
                img_name = result['image_name']
                size = result['size']
                mae = result['mae']
                
                # Update row for this image
                mask = train_df['image_name'] == img_name
                if any(mask):  # Check if image exists in the dataframe
                    train_df.loc[mask, f"{column_prefix}_size_bytes"] = size
                    
                    # Calculate bits per pixel correctly
                    num_pixels = train_df.loc[mask, 'num_pixels'].values[0]
                    bpp = (size * 8) / num_pixels
                    train_df.loc[mask, f"{column_prefix}_bpp"] = bpp
                    
                    # Calculate fitness (improvement over baseline in bytes)
                    baseline_size = train_df.loc[mask, 'baseline_size_bytes'].values[0]
                    fitness = baseline_size - size
                    train_df.loc[mask, f"{column_prefix}_fitness"] = fitness
                    
                    train_df.loc[mask, f"{column_prefix}_mae"] = mae
        
        # Write updated dataframe back to Excel
        with pd.ExcelWriter(excel_path, mode='a', if_sheet_exists='replace') as writer:
            train_df.to_excel(writer, sheet_name='Training', index=False)
        
        return True
    except Exception as e:
        print(f"Error updating training sheet: {e}")
        return False


def update_with_wop8_results(excel_path, wop8_results):
    """
    Update testing and all images sheets with W-OP8 results.
    
    Args:
        excel_path (str): Path to the Excel file
        wop8_results (dict): Dictionary with W-OP8 results
            {
                'results': [
                    {
                        'image_name': 'img1.png', 
                        'size': 1000, 
                        'mae': 0.0
                    },
                    ...
                ]
            }
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing Excel file
        test_df = pd.read_excel(excel_path, sheet_name='Testing')
        all_df = pd.read_excel(excel_path, sheet_name='All Images')
        
        # Update test_df with W-OP8 results
        for result in wop8_results['results']:
            img_name = result['image_name']
            size = result['size']
            mae = result['mae']
            
            # Update testing sheet
            test_mask = test_df['image_name'] == img_name
            if any(test_mask):
                test_df.loc[test_mask, 'wop8_size_bytes'] = size
                test_df.loc[test_mask, 'wop8_mae'] = mae
                
                # Calculate derived metrics
                baseline_size = test_df.loc[test_mask, 'baseline_size_bytes'].values[0]
                num_pixels = test_df.loc[test_mask, 'num_pixels'].values[0]
                
                # Calculate W-OP8 bits per pixel correctly
                wop8_bpp = (size * 8) / num_pixels
                test_df.loc[test_mask, 'wop8_bpp'] = wop8_bpp
                
                # Calculate difference vs baseline
                size_reduction = baseline_size - size
                test_df.loc[test_mask, 'size_reduction_bytes'] = size_reduction
                
                # Calculate bpp improvement
                baseline_bpp = test_df.loc[test_mask, 'baseline_bpp'].values[0]
                bpp_improvement = baseline_bpp - wop8_bpp
                test_df.loc[test_mask, 'bpp_improvement'] = bpp_improvement
                
                # Calculate improvement percentage
                improvement_percentage = (size_reduction / baseline_size) * 100
                test_df.loc[test_mask, 'improvement_percentage'] = improvement_percentage
            
            # Update all images sheet
            all_mask = all_df['image_name'] == img_name
            if any(all_mask):
                all_df.loc[all_mask, 'wop8_size_bytes'] = size
                all_df.loc[all_mask, 'wop8_mae'] = mae
                
                # Calculate derived metrics
                baseline_size = all_df.loc[all_mask, 'baseline_size_bytes'].values[0]
                num_pixels = all_df.loc[all_mask, 'num_pixels'].values[0]
                
                # Calculate W-OP8 bits per pixel correctly
                wop8_bpp = (size * 8) / num_pixels
                all_df.loc[all_mask, 'wop8_bpp'] = wop8_bpp
                
                # Calculate difference vs baseline
                size_reduction = baseline_size - size
                all_df.loc[all_mask, 'size_reduction_bytes'] = size_reduction
                
                # Calculate bpp improvement
                baseline_bpp = all_df.loc[all_mask, 'baseline_bpp'].values[0]
                bpp_improvement = baseline_bpp - wop8_bpp
                all_df.loc[all_mask, 'bpp_improvement'] = bpp_improvement
                
                # Calculate improvement percentage
                improvement_percentage = (size_reduction / baseline_size) * 100
                all_df.loc[all_mask, 'improvement_percentage'] = improvement_percentage
        
        # Write updated dataframes back to Excel
        with pd.ExcelWriter(excel_path, mode='a', if_sheet_exists='replace') as writer:
            test_df.to_excel(writer, sheet_name='Testing', index=False)
            all_df.to_excel(writer, sheet_name='All Images', index=False)
        
        return True
    except Exception as e:
        print(f"Error updating with W-OP8 results: {e}")
        return False
#
def update_spreadsheet_with_baseline(excel_path, train_results, test_results):
    """
    Update the spreadsheet with baseline compression results.
    
    Args:
        excel_path (str): Path to the Excel file
        train_results (dict): Dictionary with training results {image_name: {size, mae}}
        test_results (dict): Dictionary with testing results {image_name: {size, mae}}
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing Excel file
        train_df = pd.read_excel(excel_path, sheet_name='Training')
        test_df = pd.read_excel(excel_path, sheet_name='Testing')
        all_df = pd.read_excel(excel_path, sheet_name='All Images')
        
        # Store total rows before updating
        train_total = train_df[train_df['image_name'] == 'TOTAL'].copy() if 'TOTAL' in train_df['image_name'].values else None
        test_total = test_df[test_df['image_name'] == 'TOTAL'].copy() if 'TOTAL' in test_df['image_name'].values else None
        all_total = all_df[all_df['image_name'] == 'TOTAL'].copy() if 'TOTAL' in all_df['image_name'].values else None
        
        # Remove total rows for updating
        train_df = train_df[train_df['image_name'] != 'TOTAL']
        test_df = test_df[test_df['image_name'] != 'TOTAL']
        all_df = all_df[all_df['image_name'] != 'TOTAL']
        
        # Update training sheet
        for img_name, result in train_results.items():
            mask = train_df['image_name'] == img_name
            if any(mask):
                compressed_size = result['size']
                mae = result['mae']
                
                train_df.loc[mask, 'baseline_size_bytes'] = compressed_size
                train_df.loc[mask, 'baseline_mae'] = mae
                
                # Calculate bits per pixel
                num_pixels = train_df.loc[mask, 'num_pixels'].values[0]
                bpp = (compressed_size * 8) / num_pixels
                train_df.loc[mask, 'baseline_bpp'] = bpp
                
                # Update all_df as well
                all_mask = all_df['image_name'] == img_name
                if any(all_mask):
                    all_df.loc[all_mask, 'baseline_size_bytes'] = compressed_size
                    all_df.loc[all_mask, 'baseline_mae'] = mae
                    all_df.loc[all_mask, 'baseline_bpp'] = bpp
        
        # Update testing sheet
        for img_name, result in test_results.items():
            mask = test_df['image_name'] == img_name
            if any(mask):
                compressed_size = result['size']
                mae = result['mae']
                
                test_df.loc[mask, 'baseline_size_bytes'] = compressed_size
                test_df.loc[mask, 'baseline_mae'] = mae
                
                # Calculate bits per pixel
                num_pixels = test_df.loc[mask, 'num_pixels'].values[0]
                bpp = (compressed_size * 8) / num_pixels
                test_df.loc[mask, 'baseline_bpp'] = bpp
                
                # Update all_df as well
                all_mask = all_df['image_name'] == img_name
                if any(all_mask):
                    all_df.loc[all_mask, 'baseline_size_bytes'] = compressed_size
                    all_df.loc[all_mask, 'baseline_mae'] = mae
                    all_df.loc[all_mask, 'baseline_bpp'] = bpp
        
        # Calculate and add totals back
        # Training totals
        if train_total is not None:
            # Calculate new totals
            train_total_row = pd.DataFrame({
                'image_name': ['TOTAL'],
                'width': [None],
                'height': [None],
                'num_pixels': [train_df['num_pixels'].sum()],
                'uncompressed_size_bytes': [train_df['uncompressed_size_bytes'].sum()],
                'baseline_size_bytes': [train_df['baseline_size_bytes'].sum()],
                'baseline_bpp': [train_df['baseline_bpp'].mean()],
                'baseline_mae': [train_df['baseline_mae'].mean()]
            })
            # Add other columns that may exist
            for col in train_df.columns:
                if col not in train_total_row.columns:
                    train_total_row[col] = None
            train_df = pd.concat([train_df, train_total_row], ignore_index=True)
        
        # Testing totals
        if test_total is not None:
            # Calculate new totals
            test_total_row = pd.DataFrame({
                'image_name': ['TOTAL'],
                'width': [None],
                'height': [None],
                'num_pixels': [test_df['num_pixels'].sum()],
                'uncompressed_size_bytes': [test_df['uncompressed_size_bytes'].sum()],
                'baseline_size_bytes': [test_df['baseline_size_bytes'].sum()],
                'baseline_bpp': [test_df['baseline_bpp'].mean()],
                'baseline_mae': [test_df['baseline_mae'].mean()]
            })
            # Add other columns that may exist
            for col in test_df.columns:
                if col not in test_total_row.columns:
                    test_total_row[col] = None
            test_df = pd.concat([test_df, test_total_row], ignore_index=True)
        
        # All images totals
        if all_total is not None:
            # Calculate new totals
            all_total_row = pd.DataFrame({
                'image_name': ['TOTAL'],
                'width': [None],
                'height': [None],
                'num_pixels': [all_df['num_pixels'].sum()],
                'uncompressed_size_bytes': [all_df['uncompressed_size_bytes'].sum()],
                'baseline_size_bytes': [all_df['baseline_size_bytes'].sum()],
                'baseline_bpp': [all_df['baseline_bpp'].mean()],
                'baseline_mae': [all_df['baseline_mae'].mean()]
            })
            # Add other columns that may exist
            for col in all_df.columns:
                if col not in all_total_row.columns:
                    all_total_row[col] = None
            all_df = pd.concat([all_df, all_total_row], ignore_index=True)
        
        # Write updated dataframes back to Excel
        with pd.ExcelWriter(excel_path, mode='a', if_sheet_exists='replace') as writer:
            train_df.to_excel(writer, sheet_name='Training', index=False)
            test_df.to_excel(writer, sheet_name='Testing', index=False)
            all_df.to_excel(writer, sheet_name='All Images', index=False)
        
        return True
    except Exception as e:
        print(f"Error updating spreadsheet with baseline results: {e}")
        return False