# src/compression/wop8.py
import os
import sys
from tqdm import tqdm

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import CONTEXT_PREDICT_PATH, BUILD_DIR, COMPRESSED_DIR

from src.compression.context_manager import ContextFileManager
from src.compression.baseline import BaselineCompression

class WOP8Compression:
    """
    Handles W-OP8 compression operations with optimized weights.
    """
    
    def __init__(self):
        """Initialize the W-OP8 compression handler"""
        self.context_manager = ContextFileManager(CONTEXT_PREDICT_PATH, BUILD_DIR)
        self.baseline_compressor = BaselineCompression()  # Reuse compression functionality
    
    def setup_with_best_weights(self, best_weights):
        """
        Set up W-OP8 with the best weights found by GA.
        
        Args:
            best_weights (list): List of 8 integer weights found by GA
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure versions exist
        self.context_manager.ensure_versions_exist()
        
        # Switch to W-OP8 implementation
        success = self.context_manager.use_wop8()
        if not success:
            return False
        
        # Update weights
        success = self.context_manager.update_wop8_weights(best_weights)
        if not success:
            return False
        
        # Rebuild library
        return self.context_manager.rebuild_library()
    
    def compress_dataset(self, image_paths, dataset_name):
        """
        Compress a dataset using W-OP8 with the optimized weights.
        
        Args:
            image_paths (list): List of paths to images
            dataset_name (str): Name of the dataset
            
        Returns:
            dict: Dictionary with compression results
        """
        # Set up output directories
        compressed_dir = os.path.join(COMPRESSED_DIR, dataset_name, 'wop8')
        decompressed_dir = os.path.join(COMPRESSED_DIR, dataset_name, 'wop8_decompressed')
        
        os.makedirs(compressed_dir, exist_ok=True)
        os.makedirs(decompressed_dir, exist_ok=True)
        
        # Compress images
        results = {}
        
        for input_path in tqdm(image_paths, desc=f"Compressing {dataset_name} with W-OP8"):
            image_name = os.path.basename(input_path)
            compressed_path = os.path.join(compressed_dir, f"{os.path.splitext(image_name)[0]}.jxl")
            decompressed_path = os.path.join(decompressed_dir, image_name)
            
            # Use the same compression function from BaselineCompression
            result = self.baseline_compressor.compress_image(input_path, compressed_path, decompressed_path)
            if result:
                results[image_name] = result
        
        return results