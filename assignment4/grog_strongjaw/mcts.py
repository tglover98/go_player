from board_util import GoBoardUtil, EMPTY
from simple_board import SimpleGoBoard

import random
import numpy as np

def undo(board,move):
    board.board[move]=EMPTY
    board.current_player=GoBoardUtil.opponent(board.current_player)

def uct_val(node, child, C, max_flag):
    if child.visits == 0:
        return float("inf")
    if max_flag:
        return float(child.wins) / child.visits + C *np.sqrt(
            np.log(node.visits) / child.visits
        )
    else:
        return float( child.vists - child.wins) / child.visits + C * np.sqrt(
            np.log(node.visits) / child.visits)
def game_result(board):
    game_end, winner = board.check_game_end_gomoku()
    moves = board.get_empty_points()
    board_full = (len(moves) == 0)
    if game_end:
        #return 1 if winner == board.current_player else -1
        return winner
    if board_full:
        return 'draw'
    return None


class MCTS(object):
    def __init__(self, color):
        self.num_sim = 1
        self.root = TreeNode(None)
        self.my_color = color
        self.exploration = 1
    
    def build_tree(self, board):
        assert board.current_player == self.my_color
        while True:
            board_copy = board.copy()
            toplay = board.current_player
            self.playout(board_copy, toplay)

    
    def get_best_move(self):
        moves_ls = [
            (move, node.visits) for move, node in self.root.children.items()
        ]
        if not moves_ls:
            return None
        moves_ls = sorted(moves_ls, key=lambda i: i[1], reverse=True)
        move = moves_ls[0]
        return move[0]
    
    def playout(self, board, toplay):
        node = self.root
        count = 0
        color =  self.my_color
        if not node.expanded:
            node.expand(board)
        while not node.is_leaf():
            count +=1
            max_flag = toplay == self.my_color
            move, next_node = node.select(self.exploration, max_flag)
            color = board.current_player
            board.play_move(move, color)
            color = board.current_player
            node = next_node
            if count >50:
                self.exploration = 1
        assert node.is_leaf()
        if not node.expanded:
            node.expand(board)
        assert board.current_player == color
        leaf_value = self.simulate(board)
        node.update_recursive(leaf_value)

    def simulate(self, board):
        result = game_result(board)
        simulation_moves = []
        while(result is None):
            ret = board.get_pattern_moves()
            if ret == None:
                moves = GoBoardUtil.generate_legal_moves_gomoku(board)
            else:
                movetype_id, moves=ret

            playout_move = random.choice(moves)
            board.play_move_gomoku(playout_move, board.current_player)
            simulation_moves.append(playout_move)
            result = game_result(board)
            for m in simulation_moves[::-1]:
                undo(board, m)
        if result == self.my_color:
            return 1
        else:
            return 0
        

class TreeNode(object):
    def __init__(self,parent):
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.wins = 0
        self.expanded = False
        self.move = None

    def expand(self, board):
        ret = board.get_pattern_moves()
        if ret == None:
            moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        else:
            movetype_id, moves=ret
        legal_moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        if moves == None:
            moves = legal_moves
        for move in moves:
            if move not in self.children:
                if move in legal_moves:
                    self.children[move] = TreeNode(self)
                    self.children[move].move = move
        self.expanded = True
    
    def select(self, exploration, max_flag):
        return max(
            self.children.items(),
            key=lambda items: uct_val(self, items[1], exploration, max_flag),
        )
    def update(self, leaf_value):
        self.wins += leaf_value
        self.visits += 1

    def update_recursive(self, leaf_value):
        if self.parent:
            self.parent.update_recursive(leaf_value)
        self.update(leaf_value)

    def is_leaf(self):
        return self.children == {}

    def is_root(self):
        return self.parent is None