"""
Simplified Chess Cheating Detection System with Player Filtering
"""

import chess
import chess.pgn
import chess.engine
import numpy as np
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
import json
import warnings
warnings.filterwarnings('ignore')

class SimpleCheatDetector:
    """Main cheating detection class with player filtering"""
    
    def __init__(self, engine_path: str = None):
        """
        Initialize detector
        
        Args:
            engine_path: Path to Stockfish engine (if None, uses basic analysis without engine)
        """
        self.engine = None
        if engine_path:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
                print(f"Engine loaded from: {engine_path}")
            except Exception as e:
                print(f"Warning: Could not load engine: {e}")
                print("Will use basic analysis only")
                self.engine = None
    
    def __del__(self):
        """Clean up engine"""
        if self.engine:
            self.engine.quit()
    
    def analyze_pgn_file(self, pgn_file: str, 
                         target_player: str = None,
                         side: str = None) -> Dict[str, Any]:
        """
        Analyze all games in a PGN file with player filtering
        
        Args:
            pgn_file: Path to PGN file
            target_player: Username/name of player to analyze (optional)
            side: Which side to analyze - 'white', 'black', or None for both (optional)
            
        Returns:
            Dictionary with analysis results
        """
        games = []
        with open(pgn_file) as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                # Filter games by player if specified
                if target_player:
                    white = game.headers.get('White', '')
                    black = game.headers.get('Black', '')
                    
                    # Skip if target player not in this game
                    if target_player.lower() not in [white.lower(), black.lower()]:
                        continue
                
                games.append(game)
        
        if not games:
            print(f"No games found matching criteria")
            return {'error': 'No matching games found'}
        
        print(f"Analyzing {len(games)} games...")
        
        results = []
        for i, game in enumerate(games):
            print(f"  Analyzing game {i+1}/{len(games)}...")
            analysis = self.analyze_game(game, target_player, side)
            results.append(analysis)
        
        # Aggregate results
        return self.aggregate_results(results, pgn_file, target_player, side)
    
    def analyze_game(self, game: chess.pgn.Game, 
                     target_player: str = None,
                     side: str = None) -> Dict[str, Any]:
        """
        Analyze a single game with player/side filtering
        
        Args:
            game: python-chess Game object
            target_player: Username/name of player to analyze
            side: Which side to analyze - 'white', 'black', or None for both
            
        Returns:
            Dictionary with game analysis
        """
        board = game.board()
        moves = list(game.mainline_moves())
        
        if len(moves) < 5:
            return {
                'error': 'Game too short',
                'moves': len(moves)
            }
        
        # Determine which player we're analyzing
        white_player = game.headers.get('White', 'Unknown')
        black_player = game.headers.get('Black', 'Unknown')
        
        # Determine side to analyze
        analyze_white = False
        analyze_black = False
        
        if target_player:
            # Analyze only the target player's moves
            if target_player.lower() == white_player.lower():
                analyze_white = True
                analyze_black = False
                analyzed_player = white_player
                analyzed_side = 'white'
            elif target_player.lower() == black_player.lower():
                analyze_white = False
                analyze_black = True
                analyzed_player = black_player
                analyzed_side = 'black'
            else:
                # Should not happen due to filtering, but just in case
                return {'error': f'Target player {target_player} not in this game'}
        elif side:
            # Analyze specific side regardless of player name
            if side.lower() == 'white':
                analyze_white = True
                analyze_black = False
                analyzed_player = white_player
                analyzed_side = 'white'
            elif side.lower() == 'black':
                analyze_white = False
                analyze_black = True
                analyzed_player = black_player
                analyzed_side = 'black'
            else:
                analyze_white = True
                analyze_black = True
                analyzed_player = 'Both'
                analyzed_side = 'both'
        else:
            # Analyze both sides
            analyze_white = True
            analyze_black = True
            analyzed_player = 'Both'
            analyzed_side = 'both'
        
        # Analyze moves
        move_analyses = []
        move_number = 1
        
        for i, move in enumerate(moves):
            # Determine which side is making this move
            is_white_move = (i % 2 == 0)
            
            # Check if we should analyze this move
            analyze_this_move = False
            if is_white_move and analyze_white:
                analyze_this_move = True
            elif not is_white_move and analyze_black:
                analyze_this_move = True
            
            if analyze_this_move:
                move_analysis = self.analyze_move(board, move, move_number, is_white_move)
                move_analyses.append(move_analysis)
                move_number += 1
            
            # Always push the move regardless of analysis
            board.push(move)
        
        # Calculate game-level metrics
        return self.calculate_game_metrics(game, move_analyses, 
                                          analyzed_player, analyzed_side)
    
    def analyze_move(self, board: chess.Board, move: chess.Move, 
                     move_num: int, is_white: bool) -> Dict[str, Any]:
        """
        Analyze a single move
        
        Args:
            board: Current board position
            move: Move to analyze
            move_num: Move number
            is_white: Whether this is a white move
            
        Returns:
            Dictionary with move analysis
        """
        analysis = {
            'move_number': move_num,
            'san': board.san(move),
            'fen': board.fen(),
            'side': 'white' if is_white else 'black'
        }
        
        # Basic move evaluation without engine
        if self.engine:
            try:
                # Analyze position before move
                before_analysis = self.engine.analyse(board, chess.engine.Limit(time=0.1))
                before_eval = before_analysis['score'].relative.score(mate_score=10000)
                
                # Make move and analyze
                board_copy = board.copy()
                board_copy.push(move)
                after_analysis = self.engine.analyse(board_copy, chess.engine.Limit(time=0.1))
                after_eval = after_analysis['score'].relative.score(mate_score=10000)
                
                # Get best move
                best_move = before_analysis.get('pv', [None])[0]
                
                # Calculate metrics
                analysis['evaluation_before'] = before_eval / 100 if before_eval else 0
                analysis['evaluation_after'] = after_eval / 100 if after_eval else 0
                analysis['is_best_move'] = (best_move == move) if best_move else False
                
                # Calculate centipawn loss
                if best_move:
                    best_board = board.copy()
                    best_board.push(best_move)
                    best_eval = self.engine.analyse(best_board, chess.engine.Limit(time=0.1))
                    best_score = best_eval['score'].relative.score(mate_score=10000)
                    
                    if best_score is not None and after_eval is not None:
                        analysis['centipawn_loss'] = abs(best_score - after_eval) / 100
                    else:
                        analysis['centipawn_loss'] = 0
                else:
                    analysis['centipawn_loss'] = 0
                
                # Calculate accuracy (0-100)
                if analysis['centipawn_loss'] < 0.5:
                    analysis['accuracy'] = 100
                elif analysis['centipawn_loss'] < 1:
                    analysis['accuracy'] = 95
                elif analysis['centipawn_loss'] < 2:
                    analysis['accuracy'] = 85
                elif analysis['centipawn_loss'] < 3:
                    analysis['accuracy'] = 70
                elif analysis['centipawn_loss'] < 5:
                    analysis['accuracy'] = 50
                else:
                    analysis['accuracy'] = max(0, 100 - analysis['centipawn_loss'] * 10)
                
            except Exception as e:
                analysis['error'] = str(e)
        
        return analysis
    
    def calculate_game_metrics(self, game: chess.pgn.Game, 
                               move_analyses: List[Dict],
                               analyzed_player: str,
                               analyzed_side: str) -> Dict[str, Any]:
        """
        Calculate comprehensive game metrics
        """
        if not move_analyses:
            return {'error': 'No moves analyzed'}
        
        # Extract basic game info
        headers = game.headers
        result = headers.get('Result', '*')
        white_player = headers.get('White', 'Unknown')
        black_player = headers.get('Black', 'Unknown')
        
        # Calculate accuracy metrics
        accuracies = [m.get('accuracy', 0) for m in move_analyses if 'accuracy' in m]
        centipawn_losses = [m.get('centipawn_loss', 0) for m in move_analyses if 'centipawn_loss' in m]
        
        # Determine game phases based on move count
        total_moves = len(move_analyses)
        opening_moves = move_analyses[:min(10, total_moves)]  # First 10 moves of analyzed player
        middlegame_moves = move_analyses[10:min(40, total_moves)] if total_moves > 10 else []
        endgame_moves = move_analyses[40:] if total_moves > 40 else []
        
        # Calculate metrics
        metrics = {
            'game_id': headers.get('Site', 'Unknown'),
            'date': headers.get('Date', 'Unknown'),
            'white': white_player,
            'black': black_player,
            'result': result,
            'analyzed_player': analyzed_player,
            'analyzed_side': analyzed_side,
            'total_moves_analyzed': len(move_analyses),
            'total_game_moves': total_moves,
            
            # Accuracy metrics
            'overall_accuracy': np.mean(accuracies) if accuracies else 0,
            'opening_accuracy': np.mean([m['accuracy'] for m in opening_moves if 'accuracy' in m]) if opening_moves else 0,
            'middlegame_accuracy': np.mean([m['accuracy'] for m in middlegame_moves if 'accuracy' in m]) if middlegame_moves else 0,
            'endgame_accuracy': np.mean([m['accuracy'] for m in endgame_moves if 'accuracy' in m]) if endgame_moves else 0,
            
            # Engine correlation
            'engine_match_rate': np.mean([1 if m.get('is_best_move', False) else 0 for m in move_analyses]) if move_analyses else 0,
            
            # Error metrics
            'avg_centipawn_loss': np.mean(centipawn_losses) if centipawn_losses else 0,
            'max_centipawn_loss': np.max(centipawn_losses) if centipawn_losses else 0,
            'blunder_count': len([c for c in centipawn_losses if c > 3]),
            'mistake_count': len([c for c in centipawn_losses if 1 < c <= 3]),
            'inaccuracy_count': len([c for c in centipawn_losses if 0.5 < c <= 1]),
            
            # Consistency metrics
            'accuracy_std': np.std(accuracies) if accuracies else 0,
            'centipawn_loss_std': np.std(centipawn_losses) if centipawn_losses else 0,
            
            # Suspicious indicators
            'suspicion_score': 0  # Will be calculated
        }
        
        # Calculate suspicion score
        metrics['suspicion_score'] = self.calculate_suspicion_score(metrics)
        
        return metrics
    
    def calculate_suspicion_score(self, metrics: Dict) -> float:
        """
        Calculate suspicion score (0-1) based on various metrics
        """
        score = 0.0
        weights = {
            'accuracy': 0.25,
            'engine_match': 0.30,
            'blunders': 0.20,
            'consistency': 0.15,
            'phase_performance': 0.10
        }
        
        # Accuracy component (higher accuracy = more suspicious)
        if metrics['overall_accuracy'] > 95:
            score += 1.0 * weights['accuracy']
        elif metrics['overall_accuracy'] > 90:
            score += 0.7 * weights['accuracy']
        elif metrics['overall_accuracy'] > 85:
            score += 0.4 * weights['accuracy']
        elif metrics['overall_accuracy'] > 80:
            score += 0.2 * weights['accuracy']
        
        # Engine match rate component
        if metrics['engine_match_rate'] > 0.8:
            score += 1.0 * weights['engine_match']
        elif metrics['engine_match_rate'] > 0.7:
            score += 0.7 * weights['engine_match']
        elif metrics['engine_match_rate'] > 0.6:
            score += 0.4 * weights['engine_match']
        elif metrics['engine_match_rate'] > 0.5:
            score += 0.2 * weights['engine_match']
        
        # Blunder component (fewer blunders = more suspicious)
        if metrics['blunder_count'] == 0:
            score += 1.0 * weights['blunders']
        elif metrics['blunder_count'] == 1:
            score += 0.5 * weights['blunders']
        elif metrics['blunder_count'] <= 2:
            score += 0.2 * weights['blunders']
        
        # Consistency component (consistent high performance = suspicious)
        if metrics['accuracy_std'] < 5:
            score += 1.0 * weights['consistency']
        elif metrics['accuracy_std'] < 10:
            score += 0.5 * weights['consistency']
        elif metrics['accuracy_std'] < 15:
            score += 0.2 * weights['consistency']
        
        # Phase performance (consistent across phases)
        if metrics['opening_accuracy'] > 85 and metrics['middlegame_accuracy'] > 85 and metrics['endgame_accuracy'] > 85:
            score += 1.0 * weights['phase_performance']
        elif metrics['opening_accuracy'] > 80 and metrics['middlegame_accuracy'] > 80:
            score += 0.5 * weights['phase_performance']
        
        return min(1.0, score)
    
    def aggregate_results(self, results: List[Dict], filename: str, 
                         target_player: str = None, side: str = None) -> Dict[str, Any]:
        """
        Aggregate results from multiple games
        """
        # Filter out games with errors
        valid_games = [r for r in results if 'error' not in r]
        
        if not valid_games:
            return {
                'error': 'No valid games found',
                'total_games': len(results)
            }
        
        # Calculate aggregated metrics
        suspicion_scores = [g['suspicion_score'] for g in valid_games]
        accuracies = [g['overall_accuracy'] for g in valid_games]
        engine_match_rates = [g['engine_match_rate'] for g in valid_games]
        
        # Flag suspicious games
        flagged_games = []
        for i, game in enumerate(valid_games):
            if game['suspicion_score'] > 0.7:
                flagged_games.append({
                    'game_index': i,
                    'white': game['white'],
                    'black': game['black'],
                    'result': game['result'],
                    'suspicion_score': game['suspicion_score'],
                    'accuracy': game['overall_accuracy'],
                    'engine_match_rate': game['engine_match_rate']
                })
        
        # Create filter description
        filter_desc = ""
        if target_player:
            filter_desc = f" (analyzing only {target_player})"
        elif side:
            filter_desc = f" (analyzing only {side} side)"
        
        return {
            'file_analyzed': filename,
            'filter': filter_desc,
            'target_player': target_player,
            'side_analyzed': side,
            'total_games_in_file': len(results),
            'games_analyzed': len(valid_games),
            'timestamp': datetime.now().isoformat(),
            
            # Overall statistics
            'average_suspicion_score': np.mean(suspicion_scores),
            'max_suspicion_score': np.max(suspicion_scores),
            'average_accuracy': np.mean(accuracies),
            'average_engine_match': np.mean(engine_match_rates),
            
            # Risk assessment
            'risk_level': self.calculate_risk_level(np.mean(suspicion_scores)),
            
            # Flagged games
            'flagged_games': flagged_games,
            'flag_count': len(flagged_games),
            
            # Individual game analyses
            'game_analyses': valid_games
        }
    
    def calculate_risk_level(self, avg_suspicion: float) -> str:
        """Calculate overall risk level"""
        if avg_suspicion > 0.8:
            return "VERY HIGH"
        elif avg_suspicion > 0.6:
            return "HIGH"
        elif avg_suspicion > 0.4:
            return "MEDIUM"
        elif avg_suspicion > 0.2:
            return "LOW"
        else:
            return "VERY LOW"
    
    def generate_report(self, analysis: Dict, output_file: str = None) -> str:
        """
        Generate readable report from analysis
        """
        report = []
        report.append("=" * 80)
        report.append("CHESS CHEATING DETECTION REPORT")
        report.append("=" * 80)
        report.append(f"File: {analysis['file_analyzed']}")
        report.append(f"Filter: {analysis['filter']}")
        report.append(f"Date: {analysis['timestamp']}")
        report.append(f"Games in File: {analysis['total_games_in_file']}")
        report.append(f"Games Analyzed: {analysis['games_analyzed']}")
        report.append("")
        
        report.append("-" * 80)
        report.append("OVERALL ASSESSMENT")
        report.append("-" * 80)
        report.append(f"Risk Level: {analysis['risk_level']}")
        report.append(f"Average Suspicion Score: {analysis['average_suspicion_score']:.2%}")
        report.append(f"Average Accuracy: {analysis['average_accuracy']:.1f}%")
        report.append(f"Average Engine Match Rate: {analysis['average_engine_match']:.1%}")
        report.append("")
        
        if analysis['flag_count'] > 0:
            report.append("-" * 80)
            report.append(f"SUSPICIOUS GAMES ({analysis['flag_count']})")
            report.append("-" * 80)
            
            for i, game in enumerate(analysis['flagged_games'][:10], 1):
                report.append(f"\n{i}. Game {game['game_index'] + 1}")
                report.append(f"   Players: {game['white']} vs {game['black']}")
                report.append(f"   Result: {game['result']}")
                report.append(f"   Suspicion Score: {game['suspicion_score']:.2%}")
                report.append(f"   Accuracy: {game['accuracy']:.1f}%")
                report.append(f"   Engine Match Rate: {game['engine_match_rate']:.1%}")
            
            if len(analysis['flagged_games']) > 10:
                report.append(f"\n... and {len(analysis['flagged_games']) - 10} more suspicious games")
        
        # Add detailed analysis for most suspicious games
        if analysis['flagged_games']:
            most_suspicious = max(analysis['game_analyses'], 
                                 key=lambda x: x['suspicion_score'])
            
            report.append("")
            report.append("-" * 80)
            report.append("MOST SUSPICIOUS GAME DETAILS")
            report.append("-" * 80)
            report.append(f"Game: {most_suspicious['white']} vs {most_suspicious['black']}")
            report.append(f"Result: {most_suspicious['result']}")
            report.append(f"Analyzed Player: {most_suspicious['analyzed_player']} ({most_suspicious['analyzed_side']})")
            report.append(f"Moves Analyzed: {most_suspicious['total_moves_analyzed']}")
            report.append(f"\nAccuracy Metrics:")
            report.append(f"  Overall: {most_suspicious['overall_accuracy']:.1f}%")
            report.append(f"  Opening: {most_suspicious['opening_accuracy']:.1f}%")
            report.append(f"  Middlegame: {most_suspicious['middlegame_accuracy']:.1f}%")
            report.append(f"  Endgame: {most_suspicious['endgame_accuracy']:.1f}%")
            report.append(f"\nEngine Correlation:")
            report.append(f"  Best Move Match Rate: {most_suspicious['engine_match_rate']:.1%}")
            report.append(f"\nError Analysis:")
            report.append(f"  Average Centipawn Loss: {most_suspicious['avg_centipawn_loss']:.2f}")
            report.append(f"  Blunders: {most_suspicious['blunder_count']}")
            report.append(f"  Mistakes: {most_suspicious['mistake_count']}")
            report.append(f"  Inaccuracies: {most_suspicious['inaccuracy_count']}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"\nReport saved to: {output_file}")
        
        return report_text
    
    def export_json(self, analysis: Dict, output_file: str):
        """Export analysis as JSON"""
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"JSON exported to: {output_file}")
    
    def visualize(self, analysis: Dict, output_file: str = None):
        """
        Create visualizations of the analysis
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            sns.set_style("whitegrid")
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 1. Suspicion scores distribution
            scores = [g['suspicion_score'] for g in analysis['game_analyses']]
            axes[0, 0].hist(scores, bins=20, edgecolor='black', alpha=0.7)
            axes[0, 0].axvline(np.mean(scores), color='red', linestyle='--', label='Average')
            axes[0, 0].set_xlabel('Suspicion Score')
            axes[0, 0].set_ylabel('Number of Games')
            axes[0, 0].set_title(f'Distribution of Suspicion Scores{analysis["filter"]}')
            axes[0, 0].legend()
            
            # 2. Accuracy vs Engine Match Rate
            accuracies = [g['overall_accuracy'] for g in analysis['game_analyses']]
            match_rates = [g['engine_match_rate'] for g in analysis['game_analyses']]
            axes[0, 1].scatter(accuracies, match_rates, alpha=0.6)
            axes[0, 1].set_xlabel('Accuracy (%)')
            axes[0, 1].set_ylabel('Engine Match Rate')
            axes[0, 1].set_title('Accuracy vs Engine Match Rate')
            
            # 3. Game timeline
            if len(analysis['game_analyses']) > 1:
                game_numbers = list(range(1, len(analysis['game_analyses']) + 1))
                axes[1, 0].plot(game_numbers, scores, 'b-', marker='o', markersize=4)
                axes[1, 0].axhline(y=0.7, color='red', linestyle='--', label='Suspicion Threshold')
                axes[1, 0].set_xlabel('Game Number')
                axes[1, 0].set_ylabel('Suspicion Score')
                axes[1, 0].set_title('Suspicion Score by Game')
                axes[1, 0].legend()
            
            # 4. Error analysis
            blunders = [g['blunder_count'] for g in analysis['game_analyses']]
            mistakes = [g['mistake_count'] for g in analysis['game_analyses']]
            inaccuracies = [g['inaccuracy_count'] for g in analysis['game_analyses']]
            
            x = np.arange(len(analysis['game_analyses']))
            axes[1, 1].bar(x - 0.25, blunders, 0.25, label='Blunders', alpha=0.7)
            axes[1, 1].bar(x, mistakes, 0.25, label='Mistakes', alpha=0.7)
            axes[1, 1].bar(x + 0.25, inaccuracies, 0.25, label='Inaccuracies', alpha=0.7)
            axes[1, 1].set_xlabel('Game')
            axes[1, 1].set_ylabel('Count')
            axes[1, 1].set_title('Error Analysis by Game')
            axes[1, 1].legend()
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=150, bbox_inches='tight')
                print(f"Visualization saved to: {output_file}")
            else:
                plt.show()
                
        except ImportError:
            print("Matplotlib or seaborn not available. Install with: pip install matplotlib seaborn")
        except Exception as e:
            print(f"Error creating visualization: {e}")