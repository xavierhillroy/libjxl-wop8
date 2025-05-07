# src/data_processing/partitioner.py
import os
import sys
import random
import shutil

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import TRAIN_DIR, TEST_DIR

def partition_dataset(source_files, train_dir, test_dir, train_ratio=0.1, seed=42):
    """
    Randomly partition images into training and testing sets.
    
    Args:
        source_files (list): List of paths to source image files
        train_dir (str): Directory to store training images
        test_dir (str): Directory to store testing images
        train_ratio (float): Ratio of images to use for training (0.0-1.0)
        seed (int): Random seed for reproducibility
        
    Returns:
        tuple: (train_files, test_files) - Lists of paths to training and testing files
    """
    # Create output directories if they don't exist
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Clear output directories (optional, can be commented out for safety)
    for directory in [train_dir, test_dir]:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Make a copy of the files list and shuffle it
    shuffled_files = source_files.copy()
    random.shuffle(shuffled_files)
    
    # Calculate split
    train_count = max(1, int(len(shuffled_files) * train_ratio))
    
    # Split into training and testing sets
    train_files = shuffled_files[:train_count]
    test_files = shuffled_files[train_count:]
    
    # Copy files to respective directories
    train_paths = []
    for file_path in train_files:
        file_name = os.path.basename(file_path)
        dst = os.path.join(train_dir, file_name)
        shutil.copy2(file_path, dst)
        train_paths.append(dst)
        
    test_paths = []
    for file_path in test_files:
        file_name = os.path.basename(file_path)
        dst = os.path.join(test_dir, file_name)
        shutil.copy2(file_path, dst)
        test_paths.append(dst)
    
    return train_paths, test_paths

if __name__ == "__main__":
    # This is just for testing the partitioner directly
    from validator import validate_directory
    from config import INPUT_DIR
    
    dataset_name = "Kodak_Lossless_True_Color_Image_Suite"
    dataset_dir = os.path.join(INPUT_DIR, dataset_name)
    
    valid_files, _ = validate_directory(dataset_dir)
    
    if valid_files:
        train_dir = os.path.join(TRAIN_DIR, dataset_name)
        test_dir = os.path.join(TEST_DIR, dataset_name)
        
        train_paths, test_paths = partition_dataset(valid_files, train_dir, test_dir,seed=1)
        
        print(f"Partitioned {len(valid_files)} files into:")
        print(f"  - {len(train_paths)} training files ({train_dir})")
        print(f"  - {len(test_paths)} testing files ({test_dir})")
    else:
        print(f"No valid PNG files found in {dataset_dir}")