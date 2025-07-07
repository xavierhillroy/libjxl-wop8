import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"__file__: {__file__}")
print(f"Absolute path: {os.path.abspath(__file__)}")
print(f"dirname: {os.path.dirname(__file__)}")
print(f"Script dir: {SCRIPT_DIR}")

WOP8_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
print(f"WOP8 dir: {WOP8_DIR}")

script_dir = os.path.join(WOP8_DIR, 'core')
print(os.path.isfile(__file__))
print("HELLO!!".lower().endswith("!"))

print(os.getcwd())
from PIL import Image
image = Image.open("1.png")
print(Image.open("1.png"))

print(image.format)
print(image.size)
print(image.mode)
print(image.palette)
print(image.info)
print(image.filename)
print(image.format_description)
image.rotate(90).show()
