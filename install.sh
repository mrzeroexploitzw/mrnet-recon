#!/bin/bash

echo "[*] Updating system..."
pkg update -y

echo "[*] Installing dependencies..."
pkg install python git -y

echo "[*] Installing Python modules..."
pip install -r requirements.txt

echo "[+] Installation complete!"
echo "[+] Run tool: python mrnet.py"
