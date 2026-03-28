#!/usr/bin/env python
"""
Enhanced CLI with player filtering
"""

import sys
import argparse
from pathlib import Path
from cheat_detector_enhanced import SimpleCheatDetector

def main():
    parser = argparse.ArgumentParser(description='Chess Cheating Detection System - Enhanced')
    parser.add_argument('pgn_file', help='PGN file to analyze')
    parser.add_argument('--engine', '-e', help='Path to Stockfish engine (optional)')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--json', '-j', help='Export as JSON to specified file')
    parser.add_argument('--viz', '-v', help='Save visualization to file', action='store_true')
    parser.add_argument('--quiet', '-q', help='Suppress detailed output', action='store_true')
    
    # Player filtering options (only in enhanced version)
    parser.add_argument('--player', '-p', help='Analyze only this player\'s moves')
    parser.add_argument('--side', '-s', choices=['white', 'black'], 
                       help='Analyze only a specific side (white or black)')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.pgn_file).exists():
        print(f"Error: File not found: {args.pgn_file}")
        sys.exit(1)
    
    # Set engine path - HARDCODE YOUR PATH HERE
    # Change this to your actual Stockfish path
    DEFAULT_ENGINE_PATH = "C:\Users\Tatar\OneDrive\Desktop\Detector\stockfish\stockfish-windows-x86-64-avx2.exe"
    
    # Create detector
    print("Initializing enhanced detector...")
    detector = SimpleCheatDetector(engine_path=args.engine)
    
    # Analyze with filtering
    print(f"\nAnalyzing: {args.pgn_file}")
    if args.player:
        print(f"Filtering: Only analyzing moves by {args.player}")
    elif args.side:
        print(f"Filtering: Only analyzing {args.side} side")
    else:
        print("Analyzing: Both sides")
    
    analysis = detector.analyze_pgn_file(args.pgn_file, 
                                         target_player=args.player,
                                         side=args.side)
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        sys.exit(1)
    
    # Generate report
    report = detector.generate_report(analysis, args.output)
    
    if not args.quiet:
        print("\n" + report)
    
    # Export JSON if requested
    if args.json:
        detector.export_json(analysis, args.json)
    
    # Create visualization if requested
    if args.viz:
        viz_file = args.output.replace('.txt', '.png') if args.output else 'analysis.png'
        detector.visualize(analysis, viz_file)
    
    # Print summary
    if not args.quiet:
        print(f"\n{'='*40}")
        print(f"SUMMARY")
        print(f"{'='*40}")
        print(f"Risk Level: {analysis['risk_level']}")
        print(f"Games Analyzed: {analysis['games_analyzed']}/{analysis['total_games_in_file']}")
        print(f"Flagged Games: {analysis['flag_count']}")
        if analysis['flag_count'] > 0:
            print("\n⚠️  Suspicious games detected! Check the report for details.")

if __name__ == "__main__":
    main()