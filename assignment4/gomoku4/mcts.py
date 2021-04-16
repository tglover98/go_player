from gtp_connection import GtpConnection
from board_util import GoBoardUtil, EMPTY
from simple_board import SimpleGoBoard

import random
import numpy as np

def undo(board,move):
    board.board[move]=EMPTY
    board.current_player=GoBoardUtil.opponent(board.current_player)
    
def uct_val(node, child, C):
    if child.visits == 0:
        return float("inf")
    if max_flag:
        return float(child.wins) / child.visits + C *np.sqrt(
            np.log(node.visits) / child.visits
        )
    else:
        return float( child.vists - child.wins)/
                child.visits + C * np.sqrt(
                np.log(node.visits) / child.visits)

class mcst(object):
    def __init__(self, color, board_size=7):
        self.num_sim = 1
        self.root = TreeNode(None)
        self.my_color = color
    
    def build_tree(self, board):
        assert self.current_player == self.my_color
        while True:
            board_copy = board.copy()
            self.playout(board_copy, toplay)
    
    def get_best_move(self):
        moves_ls = [
            (move, node._n_visits) for move, node in self._root._children.items()
        ]
    
    def playout(self, board, toplay):
        node = self.root
        if not node.expanded:
            node.expand(board)
        while not node.is_leaf():
            max_flag = toplay == self.my_color
            move, next_node = node.select(self.exploration, max_flag)
            board.play_move(move, color)
            color = GoBoardUtil.opponent(color)
            node = next_node
        assert node.is_leaf()
        if not node.expanded:
            node.expand(board)
        assert board.current_player == color
        leaf_value = self.simulate(board,color)
        node.update_recursive(leaf_value)

    def simulate(self, board):
        res = game_result(board)
        simulation_moves = []
        while(res is None):
            moves = board.get_pattern_moves()
            if moves == None:
                moves = GoBoardUtil.generate_legal_moves_gomoku(board)
            playout_move = random.choice(candidate_moves)
            play_move(board, playout_move, board.current_player)
            simulation_moves.append(playout_move)
            results = game_result(board)
            for m in simulation_moves[::-1]:
                undo(board, m)
        if res == self.my_color:
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
        moves = board.get_pattern_moves()
        legal_moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        if moves = None:
            moves = legal_moves
        for move in moves:
            if move not in self.children:
                if move in legal_moves:
                    self.children[move] = TreeNode(self)
                    self.children[move].move = move
        self.expanded = True
    
    def select(self, exploration):
        return max(
            self._children.items(),
            key=lambda items: uct_val(self, items[1], exploration),
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