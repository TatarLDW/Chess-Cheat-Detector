#!/usr/bin/env python
"""
Quick summary of analysis results
"""

import sys
import argparse
import json
from pathlib import Path

def quick_summary(player_name, json_file=None):
    """Print quick summary of analysis"""
    
    if not json_file:
        json_file = f"{player_name}_deep_analysis.json"
    
    if not Path(json_file).exists():
        print(f"Error: {json_file} not found")
        print(f"Run deep analysis first: python deep_analysis_report.py games.pgn --player {player_name}")
        return
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*60)
    print(f"QUICK SUMMARY - {player_name}")
    print("="*60)
    
    print(f"\nRisk Level: {data['risk_level']}")
    print(f"Games Analyzed: {data['games_analyzed']}")
    print(f"Suspicious Games: {data['flag_count']}")
    print(f"Average Accuracy: {data['average_accuracy']:.1f}%")
    print(f"Average Engine Match: {data['average_engine_match']:.1%}")
    
    if data['flag_count'] > 0:
        print(f"\n⚠️  Suspicious games found! Check the deep report for details.")
        print("\nTop suspicious games:")
        sorted_games = sorted(data['game_analyses'], 
                             key=lambda x: x['suspicion_score'], 
                             reverse=True)
        for i, game in enumerate(sorted_games[:3], 1):
            print(f"  {i}. {game['white']} vs {game['black']}")
            print(f"     Suspicion: {game['suspicion_score']:.1%}, Accuracy: {game['overall_accuracy']:.1f}%")
    else:
        print("\n✅ No suspicious games detected")
    
    print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(description='Quick summary of chess analysis')
    parser.add_argument('--player', '-p', required=True, help='Player username')
    parser.add_argument('--json', '-j', help='JSON file path (optional)')
    
    args = parser.parse_args()
    
    quick_summary(args.player, args.json)

if __name__ == "__main__":
    main()