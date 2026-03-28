# Chess Cheating Detection System

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful chess cheating detection system that analyzes PGN files to identify potential engine assistance using Stockfish engine analysis.

## Features

- 🔍 **Deep Move Analysis**: Evaluates accuracy, centipawn loss, and engine correlation
- 👤 **Player Filtering**: Analyze specific players or sides (white/black)
- 📊 **Comprehensive Metrics**: Accuracy, engine match rates, error classification
- 📈 **Statistical Analysis**: Outlier detection, trend analysis, pattern recognition
- 🎨 **Visualizations**: 9-in-1 comprehensive charts
- 📄 **Multiple Outputs**: Text reports, JSON data, PNG/PDF visualizations
- ⚡ **Fast Analysis**: Optimized with caching and progress indicators

## Installation

### Prerequisites
- Python 3.7 or higher
- Stockfish chess engine (optional, for detailed analysis)

### Install Dependencies
```bash
pip install -r requirements.txt

### Download Stockfish (Optional)

-   Windows: Download from [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
    
-   Linux: `sudo apt-get install stockfish`
    
-   macOS: `brew install stockfish`
    

## Quick Start

### Basic Usage

bash

# Analyze all games
python analyze_games_enhanced.py games.pgn
# Analyze specific player
python analyze_games_enhanced.py games.pgn --player "Username"
# Generate deep analysis report
python deep_analysis_report.py games.pgn --player "Username"
# Create visualizations
python detailed_viz.py --player "Username"
# View suspicious moves in a specific game
python view_suspicious_moves.py games.pgn --player "Username" --game 1

### Complete Analysis Pipeline

bash

# 1. Deep analysis with JSON output
python deep_analysis_report.py games.pgn --player "Username"
# 2. Generate visualizations
python detailed_viz.py --player "Username"
# 3. View suspicious moves
python view_suspicious_moves.py games.pgn --player "Username" --game 1

## Output Files

File

Description

`{player}_deep_analysis.txt`

Detailed text report

`{player}_deep_analysis.json`

Complete data in JSON format

`{player}_detailed_analysis.png`

9-in-1 visualization chart

`{player}_game_X_analysis.txt`

Move-by-move analysis

## Configuration

Create `config.py` to set defaults:

python

STOCKFISH_PATH = "stockfish/stockfish-windows-x86-64-avx2.exe"
DEFAULT_PLAYER = "YourUsername"

## Understanding Results

### Suspicion Score (0-1)

-   **>0.8**: Very High - Strong evidence of engine assistance
    
-   **0.6-0.8**: High - Clear suspicious patterns
    
-   **0.4-0.6**: Medium - Some concerning indicators
    
-   **0.2-0.4**: Low - Minor anomalies
    
-   **<0.2**: Very Low - Normal playing patterns
    

### Accuracy Interpretation

-   **95-100%**: World Champion level
    
-   **85-95%**: Grandmaster level
    
-   **70-85%**: Strong club player
    
-   **<70%**: Average player
    

## Algorithms Used

-   **Minimax with Alpha-Beta Pruning** (via Stockfish)
    
-   **Centipawn Loss Calculation**
    
-   **Statistical Analysis** (Mean, Std Dev, Z-Score)
    
-   **Pattern Recognition** (Trend detection, consecutive analysis)
    
-   **Weighted Scoring Ensemble**
    

## Contributing

Contributions are welcome! Please submit pull requests or open issues.

## License

MIT License - see [LICENSE](https://license/) file for details.

## Author

Your Name - [Your GitHub Profile]

## Acknowledgments

-   [Stockfish](https://stockfishchess.org/) for the powerful chess engine
    
-   [python-chess](https://python-chess.readthedocs.io/) for excellent Python bindings
