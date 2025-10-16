#!/bin/bash
# Artisan-1 Development Setup Script
# Run this on Raspberry Pi 5 to set up the development environment

set -e  # Exit on error

echo "=================================================="
echo "Artisan-1 Robot Development Setup"
echo "=================================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    echo "Some features may not work on other platforms"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libatlas-base-dev \
    i2c-tools \
    git \
    vim \
    htop

# Enable I2C, SPI, Camera
echo "⚙️  Enabling hardware interfaces..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_camera 0

# Enable UART for serial servos
echo "📡 Configuring UART..."
if ! grep -q "enable_uart=1" /boot/config.txt; then
    echo "enable_uart=1" | sudo tee -a /boot/config.txt
fi
if ! grep -q "dtoverlay=disable-bt" /boot/config.txt; then
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
fi

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create log directory
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/calibration
mkdir -p data/recordings

# Download AI model (if not exists)
echo "🤖 Setting up AI models..."
if [ ! -f "models/mobilenet_ssd_v2.tflite" ]; then
    echo "Downloading MobileNet SSD model..."
    cd models
    wget -q https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
    unzip -q coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
    mv detect.tflite mobilenet_ssd_v2.tflite
    rm coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
    cd ..
    echo "✓ Model downloaded"
else
    echo "✓ Model already exists"
fi

# Create COCO labels if not exists
if [ ! -f "models/coco_labels.txt" ]; then
    echo "Creating COCO labels..."
    cat > models/coco_labels.txt << 'EOF'
person
bicycle
car
motorcycle
airplane
bus
train
truck
boat
traffic light
fire hydrant
stop sign
parking meter
bench
bird
cat
dog
horse
sheep
cow
elephant
bear
zebra
giraffe
backpack
umbrella
handbag
tie
suitcase
frisbee
skis
snowboard
sports ball
kite
baseball bat
baseball glove
skateboard
surfboard
tennis racket
bottle
wine glass
cup
fork
knife
spoon
bowl
banana
apple
sandwich
orange
broccoli
carrot
hot dog
pizza
donut
cake
chair
couch
potted plant
bed
dining table
toilet
tv
laptop
mouse
remote
keyboard
cell phone
microwave
oven
toaster
sink
refrigerator
book
clock
vase
scissors
teddy bear
hair drier
toothbrush
EOF
    echo "✓ Labels created"
fi

# Test I2C
echo ""
echo "🔍 Scanning I2C bus..."
sudo i2cdetect -y 1

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Reboot to apply all changes: sudo reboot"
echo "2. Connect hardware components"
echo "3. Run tests: python3 tests/test_subsystems.py"
echo "4. Run demo: python3 software/main.py"
echo ""
echo "Documentation:"
echo "- Quick Start: docs/quick_start.md"
echo "- BOM: docs/BOM.md"
echo "- Architecture: docs/software_architecture.md"
echo ""

read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi
