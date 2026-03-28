#!/usr/bin/env python
"""
Detailed visualizations - Generate comprehensive charts from analysis
"""

import sys
import argparse
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def create_detailed_viz(json_file, player_name):
    """Create detailed visualizations from analysis JSON"""
    
    if not Path(json_file).exists():
        print(f"Error: {json_file} not found")
        print(f"Please run deep analysis first:")
        print(f"python deep_analysis_report.py games.pgn --player {player_name}")
        return False
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    games = data['game_analyses']
    
    if not games:
        print("No game data found in JSON file")
        return False
    
    print(f"Creating visualizations for {len(games)} games...")
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Suspicion score timeline
    ax1 = plt.subplot(3, 3, 1)
    scores = [g['suspicion_score'] for g in games]
    game_nums = range(1, len(scores) + 1)
    ax1.plot(game_nums, scores, 'b-o', linewidth=2, markersize=8)
    ax1.axhline(y=0.7, color='red', linestyle='--', linewidth=2, label='High Suspicion')
    ax1.axhline(y=0.4, color='orange', linestyle='--', linewidth=2, label='Medium Suspicion')
    ax1.fill_between(game_nums, 0.7, max(scores) if scores else 1, alpha=0.2, color='red')
    ax1.fill_between(game_nums, 0.4, 0.7, alpha=0.2, color='orange')
    ax1.set_xlabel('Game Number', fontsize=10)
    ax1.set_ylabel('Suspicion Score', fontsize=10)
    ax1.set_title('Suspicion Score by Game', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # 2. Accuracy distribution
    ax2 = plt.subplot(3, 3, 2)
    accuracies = [g['overall_accuracy'] for g in games]
    ax2.hist(accuracies, bins=20, edgecolor='black', alpha=0.7, color='green')
    ax2.axvline(np.mean(accuracies), color='red', linestyle='--', linewidth=2, 
                label=f'Mean: {np.mean(accuracies):.1f}%')
    ax2.set_xlabel('Accuracy (%)', fontsize=10)
    ax2.set_ylabel('Number of Games', fontsize=10)
    ax2.set_title('Accuracy Distribution', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # 3. Engine match rate vs accuracy
    ax3 = plt.subplot(3, 3, 3)
    match_rates = [g['engine_match_rate'] * 100 for g in games]
    scatter = ax3.scatter(accuracies, match_rates, alpha=0.6, s=100, c=scores, 
                          cmap='RdYlGn_r', vmin=0, vmax=1)
    ax3.set_xlabel('Accuracy (%)', fontsize=10)
    ax3.set_ylabel('Engine Match Rate (%)', fontsize=10)
    ax3.set_title('Accuracy vs Engine Match Rate\n(Color = Suspicion Score)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='Suspicion Score')
    
    # 4. Error analysis
    ax4 = plt.subplot(3, 3, 4)
    blunders = [g['blunder_count'] for g in games]
    mistakes = [g['mistake_count'] for g in games]
    inaccuracies = [g['inaccuracy_count'] for g in games]
    
    x = np.arange(len(games))
    width = 0.25
    ax4.bar(x - width, blunders, width, label='Blunders', alpha=0.7, color='red')
    ax4.bar(x, mistakes, width, label='Mistakes', alpha=0.7, color='orange')
    ax4.bar(x + width, inaccuracies, width, label='Inaccuracies', alpha=0.7, color='yellow')
    ax4.set_xlabel('Game Number', fontsize=10)
    ax4.set_ylabel('Count', fontsize=10)
    ax4.set_title('Error Analysis by Game', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right', fontsize=8)
    ax4.set_xticks(x)
    ax4.set_xticklabels(game_nums)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Phase performance boxplot
    ax5 = plt.subplot(3, 3, 5)
    phases = ['Opening', 'Middlegame', 'Endgame']
    phase_data = []
    for game in games:
        phase_data.append([
            game.get('opening_accuracy', 0),
            game.get('middlegame_accuracy', 0),
            game.get('endgame_accuracy', 0)
        ])
    phase_data = np.array(phase_data)
    
    bp = ax5.boxplot(phase_data, labels=phases, patch_artist=True)
    colors_phase = ['lightblue', 'lightgreen', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors_phase):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax5.set_ylabel('Accuracy (%)', fontsize=10)
    ax5.set_title('Performance by Game Phase', fontsize=12, fontweight='bold')
    ax5.axhline(y=85, color='red', linestyle='--', linewidth=2, label='Suspicious Threshold')
    ax5.legend(loc='upper right', fontsize=8)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Risk level pie chart
    ax6 = plt.subplot(3, 3, 6)
    risk_counts = {
        'Very High\n(>80%)': len([g for g in games if g['suspicion_score'] > 0.8]),
        'High\n(60-80%)': len([g for g in games if 0.6 < g['suspicion_score'] <= 0.8]),
        'Medium\n(40-60%)': len([g for g in games if 0.4 < g['suspicion_score'] <= 0.6]),
        'Low\n(≤40%)': len([g for g in games if g['suspicion_score'] <= 0.4])
    }
    colors_risk = ['darkred', 'red', 'orange', 'green']
    wedges, texts, autotexts = ax6.pie(risk_counts.values(), labels=risk_counts.keys(), 
                                        autopct='%1.1f%%', colors=colors_risk, startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax6.set_title('Risk Level Distribution', fontsize=12, fontweight='bold')
    
    # 7. Moving average trend
    ax7 = plt.subplot(3, 3, 7)
    window = min(5, len(scores))
    if len(scores) >= window:
        moving_avg = np.convolve(scores, np.ones(window)/window, mode='valid')
        ax7.plot(range(window-1, len(scores)), moving_avg, 'b-', linewidth=3, 
                label=f'{window}-game moving avg')
        ax7.plot(scores, 'gray', alpha=0.5, linewidth=1, label='Individual games')
        ax7.axhline(y=0.7, color='red', linestyle='--', linewidth=2)
        ax7.axhline(y=0.4, color='orange', linestyle='--', linewidth=2)
        ax7.set_xlabel('Game Number', fontsize=10)
        ax7.set_ylabel('Suspicion Score', fontsize=10)
        ax7.set_title('Suspicion Trend (Moving Average)', fontsize=12, fontweight='bold')
        ax7.legend(loc='upper right', fontsize=8)
        ax7.grid(True, alpha=0.3)
        ax7.set_ylim(0, 1)
    
    # 8. Centipawn loss distribution
    ax8 = plt.subplot(3, 3, 8)
    cp_losses = [g['avg_centipawn_loss'] for g in games]
    ax8.hist(cp_losses, bins=20, edgecolor='black', alpha=0.7, color='purple')
    ax8.axvline(np.mean(cp_losses), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {np.mean(cp_losses):.2f}')
    ax8.set_xlabel('Average Centipawn Loss', fontsize=10)
    ax8.set_ylabel('Number of Games', fontsize=10)
    ax8.set_title('Centipawn Loss Distribution', fontsize=12, fontweight='bold')
    ax8.legend(fontsize=8)
    ax8.grid(True, alpha=0.3)
    
    # 9. Accuracy vs Game Length
    ax9 = plt.subplot(3, 3, 9)
    game_lengths = [g['total_moves_analyzed'] for g in games]
    ax9.scatter(game_lengths, accuracies, alpha=0.6, s=100, c=scores, cmap='RdYlGn_r', vmin=0, vmax=1)
    ax9.set_xlabel('Game Length (moves)', fontsize=10)
    ax9.set_ylabel('Accuracy (%)', fontsize=10)
    ax9.set_title('Accuracy vs Game Length\n(Color = Suspicion Score)', fontsize=12, fontweight='bold')
    ax9.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax9, label='Suspicion Score')
    
    # Main title
    plt.suptitle(f'Cheating Detection Analysis - {player_name}', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save figure
    output_file = f"{player_name}_detailed_analysis.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Visualization saved to: {output_file}")
    
    # Also save as PDF for better quality
    pdf_file = f"{player_name}_detailed_analysis.pdf"
    plt.savefig(pdf_file, format='pdf', bbox_inches='tight')
    print(f"✅ PDF version saved to: {pdf_file}")
    
    plt.close()
    
    return True

def main():
    """Main function with command line arguments"""
    
    parser = argparse.ArgumentParser(description='Generate visualization from chess analysis')
    parser.add_argument('--player', '-p', required=True, help='Player username')
    parser.add_argument('--json', '-j', help='JSON file path (optional, defaults to {player}_deep_analysis.json)')
    
    args = parser.parse_args()
    
    # Default JSON file name based on player
    json_file = args.json if args.json else f"{args.player}_deep_analysis.json"
    
    print("=" * 60)
    print("CHESS ANALYSIS VISUALIZATION GENERATOR")
    print("=" * 60)
    print(f"Player: {args.player}")
    print(f"JSON file: {json_file}")
    print()
    
    if not Path(json_file).exists():
        print(f"❌ Error: {json_file} not found")
        print(f"\nPlease run deep analysis first:")
        print(f"python deep_analysis_report.py games.pgn --player {args.player}")
        sys.exit(1)
    
    # Create visualization
    success = create_detailed_viz(json_file, args.player)
    
    if success:
        print(f"\n✅ Visualization complete!")
        print(f"📊 PNG file: {args.player}_detailed_analysis.png")
        print(f"📄 PDF file: {args.player}_detailed_analysis.pdf")
        print(f"\nTo view the visualization:")
        print(f"  - Double-click the PNG file")
        print(f"  - Or open with any image viewer")

if __name__ == "__main__":
    main()