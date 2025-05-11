#!/bin/bash

# setup.sh - Complete setup script for W-OP8
# Handles JPEG XL dependencies, build, and W-OP8 setup

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== W-OP8 Setup Script ===${NC}"
echo "This script will:"
echo "  1. Install JPEG XL dependencies"
echo "  2. Build JPEG XL library"
echo "  3. Set up W-OP8 Python environment"
echo "  4. Create necessary directories"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}Error: Unsupported operating system. This script supports Linux and macOS only.${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS${NC}"

# Check for required tools
check_requirements() {
    echo -e "\n${YELLOW}Checking requirements...${NC}"
    
    # Check for git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git is required but not installed.${NC}"
        exit 1
    fi
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
        if [[ "$OS" == "linux" ]]; then
            echo "Install with: sudo apt-get install python3 python3-pip"
        else
            echo "Install with: brew install python"
        fi
        exit 1
    fi
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}Error: pip3 is required but not installed.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All requirements met${NC}"
}

# Install JPEG XL dependencies
install_jxl_deps() {
    echo -e "\n${YELLOW}Installing JPEG XL dependencies...${NC}"
    
    if [ -f "./deps.sh" ]; then
        echo "Running JPEG XL deps.sh script..."
        chmod +x ./deps.sh
        ./deps.sh
    else
        echo -e "${RED}Error: deps.sh not found. Are you in the correct directory?${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ JPEG XL dependencies installed${NC}"
}

# Build JPEG XL
build_jxl() {
    echo -e "\n${YELLOW}Building JPEG XL...${NC}"
    
    # Create build directory
    mkdir -p build
    cd build
    
    # Configure with CMake
    echo "Configuring with CMake..."
    cmake -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_TESTING=OFF \
        -DJPEGXL_ENABLE_BENCHMARK=OFF \
        -DJPEGXL_ENABLE_EXAMPLES=OFF \
        -DJPEGXL_ENABLE_MANPAGES=OFF \
        -DJPEGXL_ENABLE_SJPEG=OFF \
        -DJPEGXL_ENABLE_PLUGINS=OFF \
        ..
    
    # Build
    echo "Building (this may take several minutes)..."
    ninja
    
    cd ..
    echo -e "${GREEN}✓ JPEG XL built successfully${NC}"
}

# Set up W-OP8 Python environment
setup_wop8() {
    echo -e "\n${YELLOW}Setting up W-OP8 Python environment...${NC}"
    
    cd W-OP8
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Create directory structure
    echo "Creating directory structure..."
    mkdir -p data/input
    mkdir -p data/output/compressed
    mkdir -p data/output/spreadsheets
    mkdir -p data/output/stats
    mkdir -p data/training
    mkdir -p data/testing
    
    cd ..
    echo -e "${GREEN}✓ W-OP8 environment set up${NC}"
}

# Main setup process
main() {
    check_requirements
    install_jxl_deps
    build_jxl
    setup_wop8
    
    echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
    echo ""
    echo "To run W-OP8:"
    echo "  cd W-OP8"
    echo "  python3 main.py"
    echo ""
    echo "Add your PNG datasets to: W-OP8/data/input/your_dataset_name/"
    echo ""
    echo "For more information, see the README.md file."
}

# Run main setup
main