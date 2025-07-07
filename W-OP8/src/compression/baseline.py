# src/compression/baseline.py
import os
import sys
import subprocess
from PIL import Image
import numpy as np
from tqdm import tqdm

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import BUILD_DIR, CONTEXT_PREDICT_PATH, COMPRESSED_DIR
from src.compression.context_manager import ContextFileManager

class BaselineCompression:
    """Handles baseline JPEG XL compression operations"""
    
    def __init__(self):
        """Initialize the baseline compression handler"""
        self.cjxl_path = os.path.join(BUILD_DIR, 'tools', 'cjxl')
        self.djxl_path = os.path.join(BUILD_DIR, 'tools', 'djxl')
        self.context_manager = ContextFileManager(CONTEXT_PREDICT_PATH, BUILD_DIR)
    
    def setup(self, clean=False):
        """Set up the environment for baseline compression"""
        # Ensure original and W-OP8 files exist
        self.context_manager.ensure_versions_exist()
        
        # Switch to original implementation
        if not self.context_manager.use_original():
            return False
        
        # Rebuild library with original weights
        return self.context_manager.rebuild_library(clean=clean)
    
    def calculate_mae(self, img1_path, img2_path):
        """
        Calculate Mean Absolute Error between two images.
        
        Args:
            img1_path (str): Path to first image
            img2_path (str): Path to second image
            
        Returns:
            float: Mean Absolute Error between the images
        """
        try:
            with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
                img1 = img1.convert("RGB")
                img2 = img2.convert("RGB")
                
                if img1.size != img2.size:
                    raise ValueError(f"Image dimensions don't match: {img1.size} vs {img2.size}")
                
                array1 = np.array(img1, dtype=np.float32)
                array2 = np.array(img2, dtype=np.float32)
                return np.mean(np.abs(array1 - array2))
        except Exception as e:
            print(f"Error calculating MAE: {e}")
            return None
    
    def compress_image(self, input_path, output_path, decompressed_path=None):
        """
        Compress an image using baseline JPEG XL and optionally decompress it.
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save compressed image
            decompressed_path (str, optional): Path to save decompressed image
            
        Returns:
            dict: Dictionary with compression results
                {
                    'size': compressed size in bytes,
                    'mae': MAE value if decompressed_path is provided
                }
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Compress image
            compress_cmd = [
                self.cjxl_path,
                input_path,
                output_path,
                "--distance=0",
                # "--modular_predictor=6",
                "--effort=7"
            ]
            
            result = subprocess.run(
                compress_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Compression failed: {result.stderr}")
                return None
            
            # Get compressed size
            compressed_size = os.path.getsize(output_path)
            
            # If decompressed path is provided, decompress and calculate MAE
            mae = None
            if decompressed_path:
                os.makedirs(os.path.dirname(decompressed_path), exist_ok=True)
                
                decompress_cmd = [
                    self.djxl_path,
                    output_path,
                    decompressed_path
                ]
                
                result = subprocess.run(
                    decompress_cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    print(f"Decompression failed: {result.stderr}")
                else:
                    mae = self.calculate_mae(input_path, decompressed_path)
            
            return {
                'size': compressed_size,
                'mae': mae
            }
        except Exception as e:
            print(f"Error compressing image: {e}")
            return None
    
    def compress_image_with_effort(self, input_path, output_path, effort=7, decompressed_path=None):
        """
        Compress an image using baseline JPEG XL with specified effort level and without predictor_mode.
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save compressed image
            effort (int): JPEG XL effort level (1-10)
            decompressed_path (str, optional): Path to save decompressed image
            
        Returns:
            dict: Dictionary with compression results
                {
                    'size': compressed size in bytes,
                    'mae': MAE value if decompressed_path is provided
                }
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Compress image - note: no modular_predictor parameter
            compress_cmd = [
                self.cjxl_path,
                input_path,
                output_path,
                "--distance=0",
                f"--effort={effort}"
            ]
            
            result = subprocess.run(
                compress_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Compression failed: {result.stderr}")
                return None
            
            # Get compressed size
            compressed_size = os.path.getsize(output_path)
            
            # If decompressed path is provided, decompress and calculate MAE
            mae = None
            if decompressed_path:
                os.makedirs(os.path.dirname(decompressed_path), exist_ok=True)
                
                decompress_cmd = [
                    self.djxl_path,
                    output_path,
                    decompressed_path
                ]
                
                result = subprocess.run(
                    decompress_cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    print(f"Decompression failed: {result.stderr}")
                else:
                    mae = self.calculate_mae(input_path, decompressed_path)
            
            return {
                'size': compressed_size,
                'mae': mae
            }
        except Exception as e:
            print(f"Error compressing image: {e}")
            return None
    
    def process_dataset(self, image_paths, run_name, decompress=True):
        """
        Process a list of images with baseline compression.
        
        Args:
            image_paths (list): List of paths to input images
            dataset_name (str): Name of the dataset (for organizing outputs)
            decompress (bool): Whether to decompress images and calculate MAE
            
        Returns:
            dict: Dictionary with compression results for each image
                {
                    'image_name1': {'size': size, 'mae': mae},
                    'image_name2': {'size': size, 'mae': mae},
                    ...
                }
        """
        compressed_dir = os.path.join(COMPRESSED_DIR, run_name, 'baseline')
        decompressed_dir = os.path.join(COMPRESSED_DIR, run_name, 'baseline_decompressed')
        
        os.makedirs(compressed_dir, exist_ok=True)
        if decompress:
            os.makedirs(decompressed_dir, exist_ok=True)
        
        results = {}
        for input_path in tqdm(image_paths, desc=f"Compressing {run_name} with baseline"):
            image_name = os.path.basename(input_path)
            
            compressed_path = os.path.join(compressed_dir, f"{os.path.splitext(image_name)[0]}.jxl")
            decompressed_path = os.path.join(decompressed_dir, image_name) if decompress else None
            
            result = self.compress_image(input_path, compressed_path, decompressed_path)
            if result:
                results[image_name] = result
        
        return results
    
    def process_dataset_with_effort(self, image_paths, run_name, effort=7, decompress=True):
        """
        Process a list of images with baseline compression at specified effort level.
        
        Args:
            image_paths (list): List of paths to input images
            run_name (str): Name of the dataset (for organizing outputs)
            effort (int): JPEG XL effort level (1-10)
            decompress (bool): Whether to decompress images and calculate MAE
            
        Returns:
            dict: Dictionary with compression results for each image
        """
        compressed_dir = os.path.join(COMPRESSED_DIR, run_name, f'baseline_effort{effort}')
        decompressed_dir = os.path.join(COMPRESSED_DIR, run_name, f'baseline_effort{effort}_decompressed')
        
        os.makedirs(compressed_dir, exist_ok=True)
        if decompress:
            os.makedirs(decompressed_dir, exist_ok=True)
        
        results = {}
        for input_path in tqdm(image_paths, desc=f"Compressing {run_name} with baseline (effort {effort})"):
            image_name = os.path.basename(input_path)
            
            compressed_path = os.path.join(compressed_dir, f"{os.path.splitext(image_name)[0]}.jxl")
            decompressed_path = os.path.join(decompressed_dir, image_name) if decompress else None
            
            result = self.compress_image_with_effort(input_path, compressed_path, effort, decompressed_path)
            if result:
                results[image_name] = result
        
        return results