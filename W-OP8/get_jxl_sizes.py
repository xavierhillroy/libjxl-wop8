import os

files = ['3.jxl', '3_second.jxl']

for filename in files:
    if os.path.isfile(filename):
        size_bytes = os.path.getsize(filename)
        size_kb = size_bytes / 1024
        print(f"{filename}: {size_bytes} bytes ({size_kb:.2f} KB)")
    else:
        print(f"{filename} not found.")