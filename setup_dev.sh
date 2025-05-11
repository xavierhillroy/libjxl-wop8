#!/bin/bash

# setup_dev.sh - Setup development environment for W-OP8

set -e

echo "Setting up W-OP8 development environment..."

# Run standard setup
./setup.sh

# Install development dependencies
cd W-OP8
echo "Installing development dependencies..."
pip3 install -r requirements-dev.txt

# Create example dataset structure
echo "Creating example dataset structure..."
mkdir -p data/input/examples/kodak_sample
mkdir -p data/input/examples/medical_sample

# Create .gitignore if it doesn't exist
if [ ! -f "../.gitignore" ]; then
    echo "Creating .gitignore..."
    cat > ../.gitignore << EOF
# Build directories
build/
*.o
*.a
*.so
*.dylib

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
env/
venv/
.env
.venv/

# W-OP8 outputs
W-OP8/data/output/
W-OP8/data/training/
W-OP8/data/testing/
W-OP8/data/input/*/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Backup files
*.bak
*.backup
EOF
fi

cd ..

echo "Development environment setup complete!"
echo ""
echo "Development tools installed:"
echo "  - pytest for testing"
echo "  - black for code formatting"
echo "  - flake8 for linting"
echo "  - mypy for type checking"
echo ""
echo "Example usage:"
echo "  # Format code"
echo "  cd W-OP8 && black src/"
echo ""
echo "  # Run tests"
echo "  cd W-OP8 && python -m pytest tests/"