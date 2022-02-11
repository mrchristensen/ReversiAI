from ast import Pass
import numpy as np
import random as rand
import reversi
import math
import copy

MAX = math.inf
MIN = -math.inf
MAX_SEARCH_DEPTH = 4
SCORE_RATIO_NORMALIZER = 100.0 / 63.0
MOBILITY_NORMALIZER = 100.0 / 13.0


class ReversiBot:
    def __init__(self, move_num):
        self.move_num = move_num

    def make_move(self, state):
        """
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
        """
        valid_moves = state.get_valid_moves()

        print("Start of AI making a move")
        # print("Number of Available Moves: ", self.get_mobility(state))
        # print("Possible Moves: ", state.get_valid_moves())
        # print("Score: ", self.get_score_ratio(state))

        score, move = self.minimax(
            copy.deepcopy(state), 0, True, MIN, MAX, MAX_SEARCH_DEPTH
        )
        print("Best Score Found: ", score)
        print("Best Move Found: ", move)

        # move = rand.choice(valid_moves) # Moves randomly...for now
        # print("move: ", move)

        return move

    # https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
    def minimax(self, state, current_depth, maximizing_player, alpha, beta, max_depth):
        # print("Start of Minimax - Depth: ", current_depth)
        # print("Maximizing Player: ", maximizing_player)
        # print("List of valid moves: ", state.get_valid_moves())

        # If max depth is reached
        if current_depth == max_depth or len(state.get_valid_moves()) == 0:
            # print("Score: ", self.heuristic(state), " at depth: ", current_depth)
            return self.heuristic(state), None

        if maximizing_player:

            # print("Start of maximize player's turn")
            best = MIN
            best_move = None

            # Recur for all possible moves for Maximizer
            for move in state.get_valid_moves():
                best_score, previous_last_move = self.minimax(
                    copy.deepcopy(state).simulate_move(move),
                    current_depth + 1,
                    False,
                    alpha,
                    beta,
                    max_depth,
                )

                if best_score > best:
                    best = best_score
                    best_move = move

                # best = max(best, best_score)
                alpha = max(alpha, best)

                # Prune if the found alpha is bigger or equal to beta
                if beta <= alpha:
                    break

            return best, best_move

        else:
            # print("Start of minamizing player's turn")
            best = MAX

            # Recur for all possible moves for Minimizer
            for move in state.get_valid_moves():
                best_score, previous_last_move = self.minimax(
                    copy.deepcopy(state).simulate_move(move),
                    current_depth + 1,
                    True,
                    alpha,
                    beta,
                    max_depth,
                )

                if best_score < best:
                    best = best_score
                    best_move = move

                # best = min(best, best_score)
                beta = min(beta, best)

                # Prune if the found best is less than or equal to alpha
                if beta <= alpha:
                    break

            return best, move

    def heuristic(self, state):
        mobility = self.get_mobility(state)
        score = self.get_score_difference(state)
        corner_weight = self.get_corner_heuristic(state)
        x_and_c_weight = self.get_x_and_c_heuristic(state)
        # todo: maybe check to see if mobility is infinity and return infinity, because that means we'll have all their pieces and instantly win
        # print("mobility: ", mobility)
        # print("score: ", score)
        # print("corner_weight: ", corner_weight)
        # print("x_and_c_weight: ", x_and_c_weight)

        return (
            (1.0) * score
            + (0.375) * mobility
            + (2.0) * corner_weight
            + (0.5) * x_and_c_weight
        )
        # return (score_ratio * SCORE_RATIO_NORMALIZER * (.75)) + (mobility * MOBILITY_NORMALIZER * (.25))

    def get_mobility(self, state):
        """
        Get the number of valid moves at this state
        """
        number_valid_moves = len(state.get_valid_moves())
        number_valid_enemy_moves = len(state.get_valid_enemy_moves())

        if number_valid_moves + number_valid_enemy_moves == 0:
            return 0

        return (
            100
            * (number_valid_moves - number_valid_enemy_moves)
            / (number_valid_moves + number_valid_enemy_moves)
        )

    def get_score_difference(self, state):
        """
        Returns the score comparted to the enemies (as a tuple)
        """
        player = state.turn
        enemy = None

        if player == 1:
            enemy = 2
        else:
            enemy = 1

        our_score = np.count_nonzero(state.board == player)
        enemy_score = np.count_nonzero(state.board == enemy)

        if enemy_score == 0:  # Make sure we are not dividing by zero
            return math.inf

        return 100 * (our_score - enemy_score) / (our_score + enemy_score)

    def get_corner_heuristic(self, state):
        corner_squares = {(0, 0), (0, 7), (7, 0), (7, 7)}
        board = state.board
        player = state.turn
        number_player_corners = 0
        number_enemy_corners = 0

        enemy = None
        if player == 1:
            enemy = 2
        else:
            enemy = 1

        for square in corner_squares:
            if board[square[0]][square[1]] == player:
                number_player_corners += 1
            elif board[square[0]][square[1]] == enemy:
                number_enemy_corners += 1

        if number_player_corners + number_enemy_corners == 0:
            return 0

        return (
            100
            * (number_player_corners - number_enemy_corners)
            / (number_player_corners + number_enemy_corners)
        )

    def get_x_and_c_heuristic(self, state):
        x_and_c_squares = {
            (1, 0),
            (0, 1),
            (1, 1),
            (6, 7),
            (7, 6),
            (6, 6),
            (0, 6),
            (7, 1),
            (6, 1),
            (0, 6),
            (1, 6),
            (1, 7),
        }
        board = state.board
        player = state.turn
        number_player_x_and_c = 0
        number_enemy_x_and_c = 0

        enemy = None
        if player == 1:
            enemy = 2
        else:
            enemy = 1

        for square in x_and_c_squares:
            if board[square[0]][square[1]] == player:
                number_player_x_and_c += 1
            elif board[square[0]][square[1]] == enemy:
                number_enemy_x_and_c += 1

        if number_player_x_and_c + number_enemy_x_and_c == 0:
            return 0

        return (
            100
            * (number_enemy_x_and_c - number_player_x_and_c)
            / (number_player_x_and_c + number_enemy_x_and_c)
        )
