# src/compression/context_manager.py
import os
import re
import shutil
import subprocess
import time

class ContextFileManager:
    """
    Manager for handling context_predict.h file switching between 
    original JPEG XL implementation and W-OP8 implementation.
    """
    
    def __init__(self, context_file_path, build_dir):
        """
        Initialize the context file manager.
        
        Args:
            context_file_path (str): Path to the active context_predict.h file
            build_dir (str): Path to JPEG XL build directory
        """
        self.context_file_path = context_file_path
        self.build_dir = build_dir
        
        # Store backup files in the same directory as the context manager
        self.manager_dir = os.path.dirname(os.path.abspath(__file__))
        self.original_file = os.path.join(self.manager_dir, "context_predict_original.h")
        self.wop8_file = os.path.join(self.manager_dir, "context_predict_wop8.h")
        
        # Regex for updating weights
        self.pattern = re.compile(
            r"^\s*(const\s+uint32_t\s+w(\d+)\s*=\s*0x)([0-9a-fA-F]+)(\s*;.*)$")
    
    def ensure_versions_exist(self):
        """
        Ensure both original and W-OP8 versions exist.
        If not, create them from the current file or specified paths.
        """
        # Check if the original context file exists
        if not os.path.exists(self.context_file_path):
            raise FileNotFoundError(f"Context file not found: {self.context_file_path}")
        
        # If original version doesn't exist, prompt user
        if not os.path.exists(self.original_file):
            print(f"Original JPEG XL implementation file not found at {self.original_file}")
            response = input("Is the current context_predict.h the original JPEG XL version? (y/n): ")
            
            if response.lower() == 'y':
                # Current is original, save it as original
                shutil.copy2(self.context_file_path, self.original_file)
                print(f"Saved original JPEG XL implementation as {self.original_file}")
                
                # Now ask for W-OP8 file
                wop8_path = input(f"Enter path to your W-OP8 implementation file (or press Enter to skip): ")
                if wop8_path and os.path.exists(wop8_path):
                    shutil.copy2(wop8_path, self.wop8_file)
                    print(f"Saved W-OP8 implementation as {self.wop8_file}")
            else:
                # Current is W-OP8, save it as wop8
                shutil.copy2(self.context_file_path, self.wop8_file)
                print(f"Saved current file as W-OP8 implementation ({self.wop8_file})")
                
                # Now ask for original file
                original_path = input(f"Enter path to original JPEG XL implementation file: ")
                if original_path and os.path.exists(original_path):
                    shutil.copy2(original_path, self.original_file)
                    print(f"Saved original JPEG XL implementation as {self.original_file}")
                else:
                    print("Warning: Original JPEG XL implementation file not provided.")
        
        # If W-OP8 version doesn't exist, prompt user
        if not os.path.exists(self.wop8_file):
            print(f"W-OP8 implementation file not found at {self.wop8_file}")
            response = input("Is the current context_predict.h your W-OP8 version? (y/n): ")
            
            if response.lower() == 'y':
                # Current is W-OP8, save it
                shutil.copy2(self.context_file_path, self.wop8_file)
                print(f"Saved W-OP8 implementation as {self.wop8_file}")
            else:
                # Ask for W-OP8 file
                wop8_path = input(f"Enter path to your W-OP8 implementation file: ")
                if wop8_path and os.path.exists(wop8_path):
                    shutil.copy2(wop8_path, self.wop8_file)
                    print(f"Saved W-OP8 implementation as {self.wop8_file}")
                else:
                    print("Warning: W-OP8 implementation file not provided.")
    
    def use_original(self):
        """
        Switch to original JPEG XL implementation for baseline testing.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.original_file):
                shutil.copy2(self.original_file, self.context_file_path)
                print(f"Switched to original JPEG XL implementation")
                return True
            else:
                print(f"Error: Original file {self.original_file} not found")
                return False
        except Exception as e:
            print(f"Error switching to original: {e}")
            return False
    
    def use_wop8(self):
        """
        Switch to W-OP8 implementation.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.wop8_file):
                shutil.copy2(self.wop8_file, self.context_file_path)
                print(f"Switched to W-OP8 implementation")
                return True
            else:
                print(f"Error: W-OP8 file {self.wop8_file} not found")
                return False
        except Exception as e:
            print(f"Error switching to W-OP8: {e}")
            return False
    
    def update_wop8_weights(self, weights):
        """
        Update the weight definitions in the current W-OP8 implementation.
        
        Args:
            weights (list): List of integer weights (0-15)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First switch to W-OP8 implementation (just to be safe)
            self.use_wop8()
            
            with open(self.context_file_path, 'r') as f:
                lines = f.readlines()

            new_lines = []
            updated_count = 0
            
            for line in lines:
                match = self.pattern.match(line)
                if match:
                    index = int(match.group(2))
                    if index < len(weights):
                        new_weight = weights[index]
                        new_hex = hex(new_weight)[2:]  # Convert weight to hex (without '0x')
                        new_line = f"{match.group(1)}{new_hex}{match.group(4)}\n"
                        new_lines.append(new_line)
                        updated_count += 1
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            with open(self.context_file_path, 'w') as f:
                f.writelines(new_lines)
            
            # Save updated version
            shutil.copy2(self.context_file_path, self.wop8_file)
                
            print(f"Updated {updated_count} weights in W-OP8 implementation")
            return True
        except Exception as e:
            print(f"Error updating weights: {e}")
            return False
    
    def rebuild_library(self, clean=False):
        """
        Rebuild the JPEG XL library after modifying source code.
        Ensures the rebuild properly incorporates changes.
        
        Returns:
            bool: True if build succeeded, False otherwise
        """
        try:
            print(f"Rebuilding JPEG XL library in {self.build_dir}...")
            
            # First, force a touch on the modified file to ensure timestamp changes
            # This helps make sure the build system recognizes the file changed
            current_time = time.time()
            os.utime(self.context_file_path, (current_time, current_time))
            
            # Run a clean build to ensure no caching issues
            if clean:
                print("Running clean build...")
                clean_result = subprocess.run(
                    ["ninja", "clean"], 
                    cwd=self.build_dir, 
                    capture_output=True,
                    text=True,
                    check=False
                )
                if clean_result.returncode != 0:
                    print(f"Clean failed: {clean_result.stderr}")
                    # Continue anyway since clean failure might be okay
            
            # Now run the full rebuild
            result = subprocess.run(
                ["ninja", "cjxl", "djxl"], 
                cwd=self.build_dir, 
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Build failed: {result.stderr}")
                return False
            
            # Verify binary timestamps to ensure they were actually rebuilt
            cjxl_path = os.path.join(self.build_dir, 'tools', 'cjxl')
            if os.path.exists(cjxl_path):
                cjxl_mtime = os.path.getmtime(cjxl_path)
                if cjxl_mtime < current_time:
                    print("Warning: cjxl binary wasn't updated during rebuild!")
                    return False
            
            print("Build succeeded and binaries were updated")
            return True
        except Exception as e:
            print(f"Error rebuilding library: {e}")
            return False