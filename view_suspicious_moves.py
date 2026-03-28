#!/usr/bin/env python
"""
Simplified Advanced Suspicious Move Analyzer - Working version
"""

import sys
import argparse
import chess
import chess.pgn
import chess.engine
import numpy as np
from pathlib import Path
import time
from typing import Dict, List, Optional, Any  # Add this import

class SimpleAdvancedAnalyzer:
    """Simplified advanced move analyzer that actually works"""
    
    def __init__(self, engine_path: str = None):
        """Initialize with engine"""
        self.engine = None
        self.has_engine = False
        
        if engine_path:
            engine_path = Path(engine_path)
            if engine_path.exists():
                try:
                    print(f"Loading engine from: {engine_path}")
                    self.engine = chess.engine.SimpleEngine.popen_uci(str(engine_path))
                    self.has_engine = True
                    print("✓ Engine loaded successfully!")
                    
                    # Quick test
                    test_board = chess.Board()
                    test_result = self.engine.analyse(test_board, chess.engine.Limit(time=0.1))
                    print("✓ Engine test passed!\n")
                    
                except Exception as e:
                    print(f"⚠️ Could not load engine: {e}")
                    print("Running in basic mode\n")
            else:
                print(f"⚠️ Engine not found at: {engine_path}")
                print("Running in basic mode\n")
        else:
            print("No engine provided - running in basic mode\n")
    
    def analyze_move_simple(self, board: chess.Board, move: chess.Move, 
                            move_num: int, player_side: str) -> Dict[str, Any]:
        """Simplified move analysis that definitely works"""
        
        move_san = board.san(move)
        
        analysis = {
            'move_number': move_num,
            'san': move_san,
            'accuracy': 0,
            'centipawn_loss': 0,
            'is_best_move': False,
            'best_move_san': None,
            'error_type': 'unknown',
            'explanations': [],
            'tactical_explanations': [],
            'material_impact': [],
            'recommendations': [],
            'is_suspicious': False
        }
        
        if not self.has_engine:
            # Basic analysis without engine
            analysis['explanations'].append("No engine available")
            return analysis
        
        try:
            # Simple analysis with timeout
            print(f"    Analyzing position...", end=" ", flush=True)
            
            # Get analysis with time limit
            info = self.engine.analyse(board, chess.engine.Limit(time=0.2))
            before_eval = info['score'].relative
            
            # Get best move
            best_move = info.get('pv', [None])[0]
            if best_move:
                analysis['best_move_san'] = board.san(best_move)
                analysis['is_best_move'] = (best_move == move)
            
            # Analyze after move
            board_copy = board.copy()
            board_copy.push(move)
            after_info = self.engine.analyse(board_copy, chess.engine.Limit(time=0.2))
            after_eval = after_info['score'].relative
            
            # Convert to pawns
            def to_pawns(score):
                if score is None:
                    return 0
                if score.is_mate():
                    return 10.0 if score.mate() > 0 else -10.0
                return score.score() / 100.0
            
            before = to_pawns(before_eval)
            after = to_pawns(after_eval)
            
            # Get best move evaluation if different
            best = before
            if best_move and best_move != move:
                best_board = board.copy()
                best_board.push(best_move)
                best_info = self.engine.analyse(best_board, chess.engine.Limit(time=0.2))
                best = to_pawns(best_info['score'].relative)
            
            # Calculate centipawn loss
            cp_loss = abs(best - after) * 100
            analysis['centipawn_loss'] = cp_loss
            
            # Calculate accuracy
            if cp_loss < 10:
                accuracy = 100
                analysis['error_type'] = 'perfect'
            elif cp_loss < 50:
                accuracy = 95
                analysis['error_type'] = 'excellent'
            elif cp_loss < 100:
                accuracy = 85
                analysis['error_type'] = 'good'
            elif cp_loss < 200:
                accuracy = 70
                analysis['error_type'] = 'decent'
            elif cp_loss < 500:
                accuracy = 50
                analysis['error_type'] = 'inaccuracy'
            elif cp_loss < 1000:
                accuracy = 30
                analysis['error_type'] = 'mistake'
            else:
                accuracy = max(0, 100 - cp_loss / 100)
                analysis['error_type'] = 'blunder'
            
            analysis['accuracy'] = accuracy
            
            # Simple material check
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    piece_names = {1: "pawn", 2: "knight", 3: "bishop", 4: "rook", 5: "queen"}
                    name = piece_names.get(captured.piece_type, "piece")
                    analysis['material_impact'].append(f"Captures a {name}")
                    analysis['tactical_explanations'].append(f"Captures {name}")
            
            # Check for check
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.is_check():
                analysis['tactical_explanations'].append("Gives check")
                if board_copy.is_checkmate():
                    analysis['tactical_explanations'].append("!!! CHECKMATE !!!")
            
            # Check for hanging piece
            if board.piece_at(move.to_square):
                attackers = board_copy.attackers(not board.turn, move.to_square)
                if attackers:
                    piece_names = {1: "pawn", 2: "knight", 3: "bishop", 4: "rook", 5: "queen"}
                    piece = board.piece_at(move.to_square)
                    name = piece_names.get(piece.piece_type, "piece")
                    analysis['material_impact'].append(f"Hangs a {name}")
                    analysis['tactical_explanations'].append(f"Leaves {name} undefended")
            
            # Check for promotion
            if move.promotion:
                promo_names = {5: "queen", 4: "rook", 3: "bishop", 2: "knight"}
                name = promo_names.get(move.promotion, "piece")
                analysis['tactical_explanations'].append(f"Promotes to {name}")
            
            # Generate explanations
            if analysis['is_best_move']:
                analysis['explanations'].append(f"✓ Best move! Accuracy: {accuracy:.0f}%")
            else:
                analysis['explanations'].append(f"⚠️ Not best move (Accuracy: {accuracy:.0f}%)")
                if analysis['best_move_san']:
                    analysis['explanations'].append(f"   Better: {analysis['best_move_san']}")
            
            # Evaluation change
            eval_change = after - before
            if player_side == 'black':
                eval_change = -eval_change
            
            if eval_change > 0.3:
                analysis['explanations'].append(f"📈 +{eval_change:.2f} pawns")
            elif eval_change < -0.3:
                analysis['explanations'].append(f"📉 {eval_change:.2f} pawns")
            
            # Centipawn loss
            if cp_loss > 0:
                analysis['explanations'].append(f"💰 Loss: {cp_loss:.0f} centipawns")
            
            # Check if suspicious
            if accuracy > 95:
                analysis['is_suspicious'] = True
                analysis['explanations'].append("⚠️ SUSPICIOUS: Very high accuracy")
            elif cp_loss < 20 and not analysis['is_best_move']:
                analysis['is_suspicious'] = True
                analysis['explanations'].append("⚠️ SUSPICIOUS: Very low error rate")
            
            print("Done")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            analysis['explanations'].append(f"Analysis failed: {str(e)[:50]}")
        
        return analysis
    
    def analyze_game(self, pgn_file: str, game_index: int, player_name: str) -> Dict[str, Any]:
        """Analyze the game"""
        
        # Read games
        print("Reading PGN file...")
        games = []
        with open(pgn_file, 'r', encoding='utf-8') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                games.append(game)
        
        print(f"Found {len(games)} games in file")
        
        if game_index > len(games):
            return {'error': f'Only {len(games)} games available'}
        
        game = games[game_index - 1]
        
        # Determine player
        white = game.headers.get('White', 'Unknown')
        black = game.headers.get('Black', 'Unknown')
        
        print(f"\nGame {game_index}: {white} vs {black}")
        
        if player_name.lower() == white.lower():
            player_side = 'white'
            print(f"Analyzing {player_name} (White)")
        elif player_name.lower() == black.lower():
            player_side = 'black'
            print(f"Analyzing {player_name} (Black)")
        else:
            return {'error': f'Player {player_name} not in this game'}
        
        # Analyze moves
        board = game.board()
        moves = list(game.mainline_moves())
        
        print(f"Total moves in game: {len(moves)}")
        print(f"Moves by {player_name}: {len(moves) // 2 if player_side == 'white' else len(moves) // 2}\n")
        
        analysis = {
            'game_info': {
                'white': white,
                'black': black,
                'result': game.headers.get('Result', '*'),
                'date': game.headers.get('Date', 'Unknown'),
                'player': player_name,
                'player_side': player_side,
                'total_moves': len(moves)
            },
            'moves': []
        }
        
        # Analyze each player move
        move_number = 1
        player_moves = []
        
        for i, move in enumerate(moves):
            is_white_move = (i % 2 == 0)
            
            if (player_side == 'white' and is_white_move) or \
               (player_side == 'black' and not is_white_move):
                
                print(f"Move {move_number}: {board.san(move)}")
                move_analysis = self.analyze_move_simple(board, move, move_number, player_side)
                analysis['moves'].append(move_analysis)
                player_moves.append(move_analysis)
                move_number += 1
            
            board.push(move)
        
        # Summary
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        
        if player_moves:
            accuracies = [m['accuracy'] for m in player_moves if m['accuracy'] > 0]
            if accuracies:
                avg_acc = np.mean(accuracies)
                print(f"Average Accuracy: {avg_acc:.1f}%")
            
            suspicious = [m for m in player_moves if m.get('is_suspicious', False)]
            if suspicious:
                print(f"\n⚠️ Suspicious moves detected: {len(suspicious)}")
                for m in suspicious[:5]:
                    print(f"  Move {m['move_number']}: {m['san']} - {m['accuracy']:.0f}%")
        
        return analysis

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description='Simple Advanced Move Analyzer')
    parser.add_argument('pgn_file', help='PGN file to analyze')
    parser.add_argument('--player', '-p', required=True, help='Player username')
    parser.add_argument('--game', '-g', type=int, required=True, help='Game number')
    parser.add_argument('--engine', '-e', help='Path to Stockfish engine')
    
    args = parser.parse_args()
    
    # Check file exists
    if not Path(args.pgn_file).exists():
        print(f"Error: File not found: {args.pgn_file}")
        sys.exit(1)
    
    print("="*60)
    print("ADVANCED MOVE ANALYZER")
    print("="*60)
    
    # Create analyzer
    analyzer = SimpleAdvancedAnalyzer(engine_path=args.engine)
    
    # Analyze
    analysis = analyzer.analyze_game(args.pgn_file, args.game, args.player)
    
    if 'error' in analysis:
        print(f"\n❌ Error: {analysis['error']}")
        sys.exit(1)
    
    # Print move details
    print("\n" + "="*60)
    print("MOVE DETAILS")
    print("="*60)
    
    for move in analysis['moves']:
        print(f"\nMove {move['move_number']}: {move['san']}")
        print(f"  Accuracy: {move['accuracy']:.0f}%")
        if move.get('centipawn_loss', 0) > 0:
            print(f"  Centipawn Loss: {move['centipawn_loss']:.0f}")
        
        if move.get('tactical_explanations'):
            print(f"  🎯 {move['tactical_explanations'][0]}")
        
        for exp in move.get('explanations', [])[:3]:
            print(f"  {exp}")
        
        if move.get('is_suspicious'):
            print(f"  ⚠️ SUSPICIOUS MOVE")
    
    # Save report
    output_file = f"{args.player}_game_{args.game}_analysis.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("ADVANCED MOVE ANALYSIS\n")
        f.write("="*60 + "\n\n")
        f.write(f"Player: {args.player}\n")
        f.write(f"Game: {analysis['game_info']['white']} vs {analysis['game_info']['black']}\n")
        f.write(f"Result: {analysis['game_info']['result']}\n\n")
        
        for move in analysis['moves']:
            f.write(f"\nMove {move['move_number']}: {move['san']}\n")
            f.write(f"  Accuracy: {move['accuracy']:.0f}%\n")
            f.write(f"  Error Type: {move.get('error_type', 'unknown')}\n")
            if move.get('tactical_explanations'):
                f.write(f"  Tactical: {', '.join(move['tactical_explanations'])}\n")
            if move.get('explanations'):
                f.write(f"  Analysis:\n")
                for exp in move['explanations']:
                    f.write(f"    {exp}\n")
    
    print(f"\n✅ Report saved to: {output_file}")

if __name__ == "__main__":
    main()