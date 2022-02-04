from ast import Pass
import numpy as np
import random as rand
import reversi
import math

MAX = math.inf
MIN = -math.inf
MAX_SEARCH_DEPTH = 3

class ReversiBot:
    def __init__(self, move_num):
        self.move_num = move_num

    def make_move(self, state):
        '''
        This is the only function that needs to be implemented for the lab!
        The bot should take a game state and return a move.

        The parameter "state" is of type ReversiGameState and has two useful
        member variables. The first is "board", which is an 8x8 numpy array
        of 0s, 1s, and 2s. If a spot has a 0 that means it is unoccupied. If
        there is a 1 that means the spot has one of player 1's stones. If
        there is a 2 on the spot that means that spot has one of player 2's
        stones. The other useful member variable is "turn", which is 1 if it's
        player 1's turn and 2 if it's player 2's turn.

        ReversiGameState objects have a nice method called get_valid_moves.
        When you invoke it on a ReversiGameState object a list of valid
        moves for that state is returned in the form of a list of tuples.

        Move should be a tuple (row, col) of the move you want the bot to make.
        '''
        valid_moves = state.get_valid_moves()

        print("Number of Available Moves: ", self.get_mobility(state))
        print("Possible Moves: ", state.get_valid_moves())
        print("Score: ", self.get_score(state))

        score, move = self.minimax(state, None, 0, True, MIN, MAX, MAX_SEARCH_DEPTH)
        print("Best Score Found: ", score)
        print("Best Move Found: ", move)

        # move = rand.choice(valid_moves) # Moves randomly...for now
        # print("move: ", move)

        return move

    # https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
    def minimax(self, state, last_move, current_depth, maximizing_player, alpha, beta, max_depth):
        # If max depth is reached
        if current_depth == max_depth:
            return self.heuristic(state.board), last_move

        if maximizing_player:
            best = MIN

            # Recur for all possible moves for Maximizer
            for move in state.get_valid_moves():
                if last_move is None:
                    last_move = move

                val = self.minimax(state.make_move(move), last_move, current_depth + 1, False, alpha, beta, max_depth)
                best = max(best, val)
                alpha = max(alpha, best)

                # Prune if the found alpha is bigger or equal to beta
                if beta <= alpha:
                    break

            return best, last_move

        else:
            best = MAX

            # Recur for all possible moves for Minimizer
            for move in state.get_valid_moves():
                if last_move is None:
                    last_move = move

                val = self.minimax(state.make_move(move), current_depth + 1, True, alpha, beta, max_depth)
                best = min(best, val)
                beta = min(beta, best)

                # Prune if the found best is less than or equal to alpha
                if beta <= alpha:
                    break

            return best, last_move

    def heuristic(self, state):
        mobility = self.get_mobility(state)
        score = self.get_score(state)

        return score + mobility

    def get_mobility(self, state):
        '''
        Get the number of valid moves at this state
        '''
        return len(state.get_valid_moves())

    def get_score(self, state):
        '''
        Returns the score comparted to the enemies (as a tuple)
        '''
        player = state.turn
        enemy = None

        if player == 1:
            enemy = 2
        else:
            enemy = 1

        our_score = np.count_nonzero(state.board == player)
        enemy_score = np.count_nonzero(state.board == enemy)

        return our_score, enemy_score

