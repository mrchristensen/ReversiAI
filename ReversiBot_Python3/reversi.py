import numpy as np
import reversi_bot
import socket
import sys
import time
import copy

class ReversiServerConnection:
    def __init__(self, host, bot_move_num):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, 3333 + bot_move_num)
        self.sock.connect(server_address)
        self.sock.recv(1024)

    def get_game_state(self):
        server_msg = self.sock.recv(1024).decode('utf-8').split('\n')

        turn = int(server_msg[0])

        # If the game is over
        if turn == -999:
            return ReversiGameState(None, turn)

        # Flip is necessary because of the way the server does indexing
        board = np.flip(np.array([int(x) for x in server_msg[4:68]]).reshape(8, 8), 0)

        return ReversiGameState(board, turn)

    def send_move(self, move):
        # The 7 - bit is necessary because of the way the server does indexing
        move_str = str(7 - move[0]) + '\n' + str(move[1]) + '\n'
        self.sock.send(move_str.encode('utf-8'))

class ReversiGame:
    def __init__(self, host, bot_move_num):
        self.bot_move_num = bot_move_num
        self.server_conn = ReversiServerConnection(host, bot_move_num)
        self.bot = reversi_bot.ReversiBot(bot_move_num)

    def play(self):
        while True:
            state = self.server_conn.get_game_state()

            # If the game is over
            if state.turn == -999:
                time.sleep(1)
                sys.exit()

            # If it is the bot's turn
            if state.turn == self.bot_move_num:
                move = self.bot.make_move(state)
                self.server_conn.send_move(move)

class ReversiGameState:
    def __init__(self, board, turn):
        self.board_dim = 8 # Reversi is played on an 8x8 board
        self.board = board
        self.turn = turn # Whose turn is it

    def capture_will_occur(self, row, col, xdir, ydir, could_capture=0):
        # We shouldn't be able to leave the board
        if not self.space_is_on_board(row, col):
            return False

        # If we're on a space associated with our turn and we have pieces
        # that could be captured return True. If there are no pieces that
        # could be captured that means we have consecutive bot pieces.
        if self.board[row, col] == self.turn:
            return could_capture != 0

        if self.space_is_unoccupied(row, col):
            return False

        return self.capture_will_occur(row + ydir,
                                       col + xdir,
                                       xdir, ydir,
                                       could_capture + 1)

    def space_is_on_board(self, row, col):
        return 0 <= row < self.board_dim and 0 <= col < self.board_dim

    def space_is_unoccupied(self, row, col):
        return self.board[row, col] == 0

    def space_is_available(self, row, col):
        return self.space_is_on_board(row, col) and \
               self.space_is_unoccupied(row, col)

    def is_valid_move(self, row, col):
        if self.space_is_available(row, col):
            # A valid move results in capture
            for xdir in range(-1, 2):
                for ydir in range(-1, 2):
                    if xdir == ydir == 0:
                        continue
                    if self.capture_will_occur(row + ydir, col + xdir, xdir, ydir):
                        return True

    def get_valid_moves(self):
        valid_moves = []

        # If the middle four squares aren't taken the remaining ones are all
        # that is available
        if 0 in self.board[3:5, 3:5]:
            for row in range(3, 5):
                for col in range(3, 5):
                    if self.board[row, col] == 0:
                        valid_moves.append((row, col))
        else:
            for row in range(self.board_dim):
                for col in range(self.board_dim):
                    if self.is_valid_move(row, col):
                        valid_moves.append((row, col))

        return valid_moves

    def make_move(self, new_move):
        print("New move position:")
        print(new_move[0], ",", new_move[1])
        newState = copy.deepcopy(self)
        newBoard = newState.board
        newBoard[new_move[0]][new_move[1]] = self.turn  # Put player's new move into the state
        print("State before captures:")
        print(newBoard)
        print("Checking up")
        newBoard = self.check_direction(newBoard, new_move, 0, 1)
        print("Checking up/right")
        newBoard = self.check_direction(newBoard, new_move, 1, 1)
        print("Checking right")
        newBoard = self.check_direction(newBoard, new_move, 1, 0)
        print("Checking down/right")
        newBoard = self.check_direction(newBoard, new_move, 1, -1)
        print("Checking down")
        newBoard = self.check_direction(newBoard, new_move, 0, -1)
        print("Checking down/left")
        newBoard = self.check_direction(newBoard, new_move, -1, -1)
        print("Checking left")
        newBoard = self.check_direction(newBoard, new_move, -1, 0)
        print("Checking up/left")
        newBoard = self.check_direction(newBoard, new_move, -1, 1)
        print("State after captures")
        print(newBoard)

        newState.board = newBoard
        return newState

    def check_direction(self, board, new_move, deltaX, deltaY):
        currentPosition = [0] * 2
        currentPosition[0] = new_move[0] + deltaX
        currentPosition[1] = new_move[1] + deltaY
        spacesToChange = []
        for i in range (0, 8):
            #check for out-of-bounds
            if(currentPosition[0] > 7 or currentPosition[0] < 0 or currentPosition[1] > 7 or currentPosition[1] < 0):
                break
            #if zero, no pieces can be captured in this direction
            if(board[currentPosition[0]][currentPosition[1]] == 0):
                break
            #if the space is not equal to our number, we add it to the list of pieces to switch & advance to the next space
            if(board[currentPosition[0]][currentPosition[1]] != self.turn):
                newSpace = (currentPosition[0], currentPosition[1])
                spacesToChange.append(newSpace)
                currentPosition[0] += deltaX
                currentPosition[1] += deltaY
            #if the space is equal to our number, we turn all the pieces inside spacesToChange
            if(board[currentPosition[0]][currentPosition[1]] == self.turn):
                self.flipPieces(board, spacesToChange)
            break

        return board
            
            



    def flipPieces(self, board, opponentStones):
        for stone in opponentStones:
            if(board[stone[0]][stone[1]] == 1):
                board[stone[0]][stone[1]] = 2
            elif(board[stone[0]][stone[1]] == 2):
                board[stone[0]][stone[1]] = 1
        return board
