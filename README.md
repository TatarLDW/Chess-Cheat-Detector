# Chess Cheating Detection System

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Wiki](https://img.shields.io/badge/docs-wiki-blue)](https://github.com/TatarLDW/chess-cheat-detector/wiki)

> Detect engine assistance in chess games with Stockfish analysis and comprehensive visualizations

## ✨ Features

- 🔍 **Deep move analysis** - Accuracy, centipawn loss, engine correlation
- 👤 **Player filtering** - Analyze specific players or sides
- 📊 **Comprehensive metrics** - 9-in-1 visualizations, error classification
- 📈 **Statistical analysis** - Pattern detection, trend analysis
- 📄 **Multiple outputs** - Text reports, JSON, PNG, PDF

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/TatarLDW/chess-cheat-detector.git
cd chess-cheat-detector

# Install dependencies
pip install -r requirements.txt

# Analyze a player
python deep_analysis_report.py games.pgn --player "Username"

# Generate visualization
python detailed_viz.py --player "Username"
