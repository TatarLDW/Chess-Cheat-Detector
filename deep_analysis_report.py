#!/usr/bin/env python
"""
Deep Analysis Report Generator - Complete working version
"""

import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from cheat_detector_enhanced import SimpleCheatDetector

def generate_deep_report(pgn_file, player_name, engine_path=None):
    """Generate comprehensive deep analysis report"""
    
    # Initialize detector
    print(f"Initializing detector for {player_name}...")
    detector = SimpleCheatDetector(engine_path=engine_path)
    
    # Analyze games
    print(f"\nAnalyzing {pgn_file} for player: {player_name}")
    analysis = detector.analyze_pgn_file(pgn_file, target_player=player_name)
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return None
    
    # Generate report text
    report = []
    report.append("=" * 80)
    report.append("DEEP CHEATING DETECTION REPORT")
    report.append("=" * 80)
    report.append(f"Player: {player_name}")
    report.append(f"File: {pgn_file}")
    report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Games Analyzed: {analysis['games_analyzed']}")
    report.append("")
    
    # Overall statistics
    report.append("-" * 80)
    report.append("OVERALL STATISTICS")
    report.append("-" * 80)
    report.append(f"Risk Level: {analysis['risk_level']}")
    report.append(f"Average Suspicion Score: {analysis['average_suspicion_score']:.2%}")
    report.append(f"Average Accuracy: {analysis['average_accuracy']:.1f}%")
    report.append(f"Average Engine Match Rate: {analysis['average_engine_match']:.1%}")
    report.append("")
    
    # Pattern analysis
    report.append("-" * 80)
    report.append("PATTERN ANALYSIS")
    report.append("-" * 80)
    
    # Check for patterns across games
    games = analysis['game_analyses']
    if games:
        accuracies = [g['overall_accuracy'] for g in games]
        high_acc_games = len([a for a in accuracies if a > 90])
        
        if high_acc_games > len(games) * 0.5:
            report.append("⚠️  HIGH ACCURACY PATTERN: More than 50% of games have >90% accuracy")
        else:
            report.append("✅ No high accuracy pattern detected")
        
        # Check engine match pattern
        match_rates = [g['engine_match_rate'] for g in games]
        high_match_games = len([m for m in match_rates if m > 0.7])
        
        if high_match_games > len(games) * 0.5:
            report.append("⚠️  HIGH ENGINE CORRELATION: >70% of moves match engine in most games")
        else:
            report.append("✅ No excessive engine correlation detected")
        
        # Check blunder pattern
        blunder_counts = [g['blunder_count'] for g in games]
        zero_blunder_games = len([b for b in blunder_counts if b == 0])
        
        if zero_blunder_games > len(games) * 0.7:
            report.append("⚠️  UNNATURAL BLUNDER PATTERN: Almost no blunders in most games")
        else:
            report.append("✅ Normal blunder pattern detected")
    
    # Suspicious games
    if analysis['flag_count'] > 0:
        report.append("\n" + "-" * 80)
        report.append(f"SUSPICIOUS GAMES ({analysis['flag_count']} games)")
        report.append("-" * 80)
        
        sorted_games = sorted(analysis['game_analyses'], 
                             key=lambda x: x['suspicion_score'], 
                             reverse=True)
        
        for idx, game in enumerate(sorted_games[:5], 1):
            if game['suspicion_score'] > 0.7:
                report.append(f"\nGame {idx}: {game['white']} vs {game['black']}")
                report.append(f"  Result: {game['result']}")
                report.append(f"  Date: {game['date']}")
                report.append(f"  Suspicion Score: {game['suspicion_score']:.2%}")
                report.append(f"  Accuracy: {game['overall_accuracy']:.1f}%")
                report.append(f"  Engine Match Rate: {game['engine_match_rate']:.1%}")
                report.append(f"  Blunders: {game['blunder_count']}")
                report.append(f"  Mistakes: {game['mistake_count']}")
                report.append(f"  Inaccuracies: {game['inaccuracy_count']}")
    
    # Cheating indicators
    report.append("\n" + "-" * 80)
    report.append("CHEATING INDICATORS")
    report.append("-" * 80)
    
    # Check selective cheating (white vs black performance)
    white_games = [g for g in games if g['analyzed_side'] == 'white']
    black_games = [g for g in games if g['analyzed_side'] == 'black']
    
    if white_games and black_games:
        white_avg = sum(g['overall_accuracy'] for g in white_games) / len(white_games)
        black_avg = sum(g['overall_accuracy'] for g in black_games) / len(black_games)
        
        if abs(white_avg - black_avg) > 15:
            report.append(f"⚠️  SELECTIVE CHEATING: Large gap between white ({white_avg:.1f}%) and black ({black_avg:.1f}%)")
        else:
            report.append(f"✅ Balanced performance: White {white_avg:.1f}% vs Black {black_avg:.1f}%")
    
    # Recommendations
    report.append("\n" + "-" * 80)
    report.append("RECOMMENDATIONS")
    report.append("-" * 80)
    
    if analysis['risk_level'] == "VERY HIGH":
        report.append("🔴 IMMEDIATE ACTION: Strong evidence of engine assistance detected")
        report.append("   - Review all flagged games manually")
        report.append("   - Consider reporting to platform administrators")
    elif analysis['risk_level'] == "HIGH":
        report.append("🟠 MODERATE SUSPICION: Clear suspicious patterns detected")
        report.append("   - Review the most suspicious games")
        report.append("   - Monitor future games for continued patterns")
    elif analysis['risk_level'] == "MEDIUM":
        report.append("🟡 CAUTION: Some concerning indicators detected")
        report.append("   - Review flagged games for context")
        report.append("   - Continue monitoring")
    else:
        report.append("🟢 NO ACTION NEEDED: No strong cheating indicators detected")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    # Save report
    report_file = f"{player_name}_deep_analysis.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"✅ Deep analysis report saved to: {report_file}")
    
    # Save JSON
    json_file = f"{player_name}_deep_analysis.json"
    with open(json_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"✅ JSON saved to: {json_file}")
    
    return report_file

def main():
    """Main function with command line arguments"""
    
    parser = argparse.ArgumentParser(description='Deep Chess Cheating Analysis')
    parser.add_argument('pgn_file', help='PGN file to analyze')
    parser.add_argument('--player', '-p', required=True, help='Player username to analyze')
    parser.add_argument('--engine', '-e', help='Path to Stockfish engine (optional)')
    
    args = parser.parse_args()
    
    # Check if PGN file exists
    if not Path(args.pgn_file).exists():
        print(f"Error: File not found: {args.pgn_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("DEEP CHEATING DETECTION ANALYSIS")
    print("=" * 80)
    
    # Set default engine path if not provided
    engine_path = args.engine
    if not engine_path:
        # Try default path
        default_engine = Path("stockfish/stockfish-windows-x86-64-avx2.exe")
        if default_engine.exists():
            engine_path = str(default_engine)
            print(f"Using default engine: {engine_path}")
    
    # Generate deep report
    report_file = generate_deep_report(args.pgn_file, args.player, engine_path)
    
    if report_file:
        print(f"\n✅ Analysis complete!")
        print(f"📄 Deep report: {report_file}")
        print(f"📊 JSON data: {args.player}_deep_analysis.json")
        print("\nNext steps:")
        print(f"1. Open {report_file} for detailed insights")
        print(f"2. Run: python quick_summary.py --player {args.player}")
        print(f"3. Run: python detailed_viz.py --player {args.player}")

if __name__ == "__main__":
    main()