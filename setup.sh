#!/bin/bash
# OMEGA QUANT - TERMUX AUTO SETUP
echo "========================================"
echo "  OMEGA QUANT MOBILE SETUP"
echo "========================================"

# Update packages
echo "[1/4] Updating packages..."
pkg update -y && pkg upgrade -y

# Install requirements
echo "[2/4] Installing Python & tools..."
pkg install python python-pip git -y

# Install Python libraries
echo "[3/4] Installing Python libraries..."
pip install numpy requests

# Download bot
echo "[4/4] Downloading bot..."
cd ~
rm -rf omega-quant-mobile
git clone https://github.com/YOUR_USER/omega-quant-mobile.git
cd omega-quant-mobile

echo ""
echo "========================================"
echo "  ✅ SETUP COMPLETE!"
echo "========================================"
echo ""
echo "  Run: cd ~/omega-quant-mobile"
echo "  Run: python bot.py"
echo ""
