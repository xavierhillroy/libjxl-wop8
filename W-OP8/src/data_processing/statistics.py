# src/data_processing/statistics.py
import os
import sys
from PIL import Image

# Add parent directory to path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def get_image_statistics(file_path):
    """
    Calculate essential statistics for an image.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        dict: Dictionary containing image statistics
    """
    stats = {
        'image_name': os.path.basename(file_path)
    }
    
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            stats['width'] = width
            stats['height'] = height
            stats['num_pixels'] = width * height
            
            # Calculate uncompressed size (in bytes)
            bits_per_pixel = {
                '1': 1,       # 1-bit black and white
                'L': 8,       # 8-bit grayscale
                'P': 8,       # 8-bit color palette
                'RGB': 24,    # 8-bit per channel (3 channels)
                'RGBA': 32,   # 8-bit per channel (4 channels)
                'CMYK': 32,   # 8-bit per channel (4 channels)
                'YCbCr': 24,  # 8-bit per channel (3 channels)
                'LAB': 24,    # 8-bit per channel (3 channels)
                'HSV': 24,    # 8-bit per channel (3 channels)
                'I': 32,      # 32-bit integer pixels
                'F': 32,      # 32-bit float pixels
            }
            
            bpp = bits_per_pixel.get(img.mode, 24)  # Default to 24 if unknown
            stats['uncompressed_size_bytes'] = (width * height * bpp) // 8
            
            return stats
    except Exception as e:
        stats['error'] = str(e)
        return stats

def collect_statistics(file_paths):
    """
    Collect statistics for a list of image files.
    
    Args:
        file_paths (list): List of paths to image files
        
    Returns:
        list: List of dictionaries containing statistics for each image
    """
    return [get_image_statistics(path) for path in file_paths]