# src/data_processing/validator.py
import os
from PIL import Image
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import INPUT_DIR, PROJECT_ROOT

def is_png(file_path):
    """
    Check if the file is a valid PNG image.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        bool: True if file is a valid PNG, False otherwise
    """
    # Basic existence check
    if not os.path.isfile(file_path):
        return False
    
    # Check extension
    if not file_path.lower().endswith('.png'):
        return False
    
    # Try to open with PIL to ensure it's a valid PNG image
    try:
        with Image.open(file_path) as img:
            return img.format == 'PNG'
    except Exception:
        return False

def validate_directory(dir_path):
    """
    Validate all images in a directory are PNGs.
    
    Args:
        dir_path (str): Path to directory containing images
        
    Returns:
        tuple: (valid_files, invalid_files) - Lists of valid and invalid file paths
    """
    valid_files = []
    invalid_files = []
    
    for filename in os.listdir(dir_path):
        if filename.startswith('.'):
            continue  # Skip hidden files
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            if is_png(file_path):
                valid_files.append(file_path)
            else:
                invalid_files.append(file_path)
    
    return valid_files, invalid_files

kodak_dataset_dir = os.path.join(INPUT_DIR, 'Kodak_Lossless_True_Color_Image_Suite')
valid_files, invalid_files = validate_directory(kodak_dataset_dir)

print(f"Found {len(valid_files)} valid PNG files")
print(f"Found {len(invalid_files)} invalid files")
for invalid_file in invalid_files:
    print(invalid_file)
