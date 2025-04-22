#!/bin/bash

# 💼 Change to the directory where this script is located
cd "$(dirname "$0")"
echo "📁 Changed to working directory: $(pwd)"
# Exit on any error
set -e

# Function to check if conda is already installed
function is_conda_installed {
    command -v conda >/dev/null 2>&1
}

# Install Miniconda for Apple Silicon if not installed
if ! is_conda_installed; then
    echo "📦 Miniconda not found. Installing Miniconda for Apple Silicon..."
    curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
    bash miniconda.sh -b -p "$HOME/miniconda"
    eval "$($HOME/miniconda/bin/conda shell.zsh hook)"
    conda init zsh
    echo "✅ Miniconda installed."
else
    echo "✅ Conda is already installed."
    eval "$(conda shell.zsh hook)"
fi

# Create conda environment if it doesn't already exist
if conda env list | grep -q "^scraper "; then
    echo "⚠️ Conda environment 'scraper' already exists. Skipping creation."
else
    echo "🐍 Creating conda environment 'scraper' with Python 3.9..."
    conda create -n scraper python=3.9 -y
fi

# Activate environment and install dependencies
echo "📦 Installing dependencies from requirements.txt..."
conda activate scraper
pip install -r requirements.txt

# Launch the Streamlit web app
echo "🚀 Launching Streamlit app..."
streamlit run app.py

