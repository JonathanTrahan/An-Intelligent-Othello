########################################################################################################################
# Name: Jonathan Trahan
# CWID: 103-50-342
# Date: 11/14/2022
# Assignment #: 3
# Description: Othello with an AI that uses the Mini-Max algorithm with alpha-beta pruning.
########################################################################################################################
from tkinter import *
from copy import deepcopy
from time import *


class Board:
    def __init__(self):
        # depth of the minimax algorith
        self.depth = 6
        # variable to set the time the AI sleeps before move
        self.sl = 0.5
        # variable for the animation speed
        self.aniSpeed = 0.05
        # variable to toggle animation
        # self.anime = False
        self.anime = True
        self.backupAnime = self.anime
        # value to check if undo
        self.UNDO = False
        # total game states examined after each move
        self.totalStates = 0
        # debug mode
        self.debug = False
        # alpha beta pruning switch
        self.pruning = True
        # Black always goes first
        # 0 is white and 1 is black
        self.player = 1
        # variable to check if its human vs human or human vs computer
        # set to either 0 or 1 to show what color the computer is
        self.computer = 0
        # value to keep track of the winner
        self.winner = "TBD"
        # bool to check if the player has no valid moves and needs to pass on their turn
        self.pass_turn = False
        # lists to store all the IDs for the shapes created on the background
        self.tiles = []
        # variable used to delete the score board
        self.score_board = 0
        # a list to store the previous boards, used to undo a move
        self.prev_boards = []
        # previous moves
        self.prev_moves = []
        # flipped tiles
        self.flippedTiles = []
        # Initializing a 8x8 matrix to keep track of the board
        self.board_matrix = [["e" for e in range(8)] for e in range(8)]

        # Initializing center values
        self.board_matrix[3][3] = "w"
        self.board_matrix[3][4] = "b"
        self.board_matrix[4][3] = "b"
        self.board_matrix[4][4] = "w"

        # create first instance of the score board
        white = 0
        black = 0
        color = "Black"
        # count the number of pieces for each color
        for r in range(8):
            for c in range(8):
                if self.board_matrix[r][c] == "w":
                    white += 1
                elif self.board_matrix[r][c] == "b":
                    black += 1

        # create and place the score board label
        score_text = f"{color}'s Turn\nWhite = {white}, Black = {black}"
        self.score_board = Label(root, text=score_text, font='Helvetica 25 bold')
        self.score_board.place(x=675, y=10, anchor=N)

        # create the undo button
        self.undoBtn = Button(root, text="Undo", font='Helvetica 25 bold', relief="raised", command=self.undoMove)
        self.undoBtn.place(x=675, y=110, anchor=N)

        # create the alpha-beta checkbox
        self.var1 = IntVar()
        self.ABCheckBox = Checkbutton(root, text='Alpha-Beta Pruning', font='Helvetica 15 bold', variable=self.var1,
                                      onvalue=1,
                                      offvalue=0, command=self.changeAlphaBeta)
        self.ABCheckBox.place(x=675, y=200, anchor=N)
        self.ABCheckBox.select()

        # create the debug checkbox
        self.var2 = IntVar()
        self.debugCheckBox = Checkbutton(root, text='Debug', font='Helvetica 15 bold', variable=self.var2, onvalue=1,
                                         offvalue=0,
                                         command=self.changeDebug)
        self.debugCheckBox.place(x=675, y=250, anchor=N)

        # create combo box for changing the depth
        # Label
        L1 = Label(root, text="Select Depth:", font='Helvetica 15 bold')
        L1.place(x=660, y=300, anchor=NE)

        # create the change depth buttons (only supports 1-5)
        x = 675
        # b0 = Button(root, text="0", font='Helvetica 9 bold', relief="raised", command=self.changeDepth0)
        # b0.place(x=x, y=300, anchor=N)
        b1 = Button(root, text="1", font='Helvetica 9 bold', relief="raised", command=self.changeDepth1)
        b1.place(x=x, y=300, anchor=N)
        b2 = Button(root, text="2", font='Helvetica 9 bold', relief="raised", command=self.changeDepth2)
        b2.place(x=x + 20, y=300, anchor=N)
        b3 = Button(root, text="3", font='Helvetica 9 bold', relief="raised", command=self.changeDepth3)
        b3.place(x=x + 40, y=300, anchor=N)
        b4 = Button(root, text="4", font='Helvetica 9 bold', relief="raised", command=self.changeDepth4)
        b4.place(x=x + 60, y=300, anchor=N)
        b5 = Button(root, text="5", font='Helvetica 9 bold', relief="raised", command=self.changeDepth5)
        b5.place(x=x + 80, y=300, anchor=N)
        b6 = Button(root, text="Animation", font='Helvetica 9 bold', relief="raised", command=self.changeAnime)
        b6.place(x=x + 80, y=400, anchor=N)
        # b7 = Button(root, text="Restart", font='Helvetica 9 bold', relief="raised", command=self.restart)
        # b7.place(x=x + 40, y=400, anchor=N)

    # function to update the board using the board matrix
    def updateBoard(self):
        # remove all the pieces and green dots
        for tile in self.tiles:
            shape_id = tile[0]
            cord = tile[1]
            if cord not in self.flippedTiles:
                background.delete(shape_id)

        # if undo
        if self.UNDO:
            background.delete("tile")
            background.delete("green_dot")

        # if animation variable is True
        if self.anime:
            # iterate through the board_matrix
            for r in range(8):
                for c in range(8):
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w" and (r, c) not in self.flippedTiles:
                        # shapeID = background.create_image(11 + (58 * r) + (2 * r), 11 + (58 * c) + (2 * c), tags=f"tile {r}-{c}", image=white_img, anchor="nw")
                        shapeID = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                          tags=f"tile {r}-{c}", image=white_img, anchor="nw")
                        self.tiles.append([shapeID, (r, c)])

                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b" and (r, c) not in self.flippedTiles:
                        # shapeID = background.create_image(11 + (58 * r) + (2 * r), 11 + (58 * c) + (2 * c), tags=f"tile {r}-{c}", image=black_img, anchor="nw")
                        shapeID = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                          tags=f"tile {r}-{c}", image=black_img, anchor="nw")
                        self.tiles.append([shapeID, (r, c)])

            if len(self.flippedTiles) > 0:
                # animation start
                animationTiles = []
                for tile in self.flippedTiles:
                    print(f"flippedTiles tile:{tile}")
                    r = tile[0]
                    c = tile[1]

                    for shape in self.tiles:
                        sID = shape[0]
                        cord = shape[1]
                        if cord == (r, c):
                            background.delete(sID)

                    # first animation 100%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        ID1 = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                      tags=f"tile {r}-{c}", image=black_img, anchor="nw")
                        animationTiles.append(ID1)
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        ID1 = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                      tags=f"tile {r}-{c}", image=white_img, anchor="nw")
                        animationTiles.append(ID1)

                    # update background
                    background.update()

                    # sleep
                    sleep(self.aniSpeed)

                    # remove animation tile
                    if len(animationTiles) > 0:
                        background.delete(animationTiles[-1])

                    # update background
                    background.update()

                    # second animation 75%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        ID2 = background.create_image(11 + (14 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=black_img_75, anchor="nw")
                        animationTiles.append(ID2)
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        ID2 = background.create_image(11 + (14 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=white_img_75, anchor="nw")
                        animationTiles.append(ID2)

                    # update background
                    background.update()

                    # sleep
                    sleep(self.aniSpeed)

                    # remove animation tile
                    if len(animationTiles) > 0:
                        background.delete(animationTiles[-1])

                    # update background
                    background.update()

                    # third animation 50%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        ID3 = background.create_image(11 + (14 / 2) + (15 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (15 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=black_img_50, anchor="nw")
                        animationTiles.append(ID3)
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        ID3 = background.create_image(11 + (14 / 2) + (15 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (15 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=white_img_50, anchor="nw")
                        animationTiles.append(ID3)

                    # update background
                    background.update()

                    # sleep
                    sleep(self.aniSpeed)

                    # remove animation tile
                    if len(animationTiles) > 0:
                        background.delete(animationTiles[-1])

                    # update background
                    background.update()

                    # fourth animation 25%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        ID4 = background.create_image(11 + (14 / 2) + (15 / 2) + (14 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (15 / 2) + (14 / 2) + (58 * r) + (2 * r),
                                                      tags=f"tile {r}-{c}", image=black_img_25, anchor="nw")
                        animationTiles.append(ID4)
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        ID4 = background.create_image(11 + (14 / 2) + (15 / 2) + (14 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (15 / 2) + (14 / 2) + (58 * r) + (2 * r),
                                                      tags=f"tile {r}-{c}", image=white_img_25, anchor="nw")
                        animationTiles.append(ID4)

                    # update background
                    background.update()

                    # sleep
                    sleep(self.aniSpeed)

                    # remove animation tile
                    if len(animationTiles) > 0:
                        background.delete(animationTiles[-1])

                    # update background
                    background.update()

                    # fifth animation 50%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        ID5 = background.create_image(11 + (14 / 2) + (15 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (15 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=white_img_50, anchor="nw")
                        animationTiles.append(ID5)
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        ID5 = background.create_image(11 + (14 / 2) + (15 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (15 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=black_img_50, anchor="nw")
                        animationTiles.append(ID5)

                    # update background
                    background.update()

                    # sleep
                    sleep(self.aniSpeed)

                    # remove animation tile
                    if len(animationTiles) > 0:
                        background.delete(animationTiles[-1])

                    # update background
                    background.update()

                    # sixth animation 75%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        ID5 = background.create_image(11 + (14 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=white_img_75, anchor="nw")
                        animationTiles.append(ID5)
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        ID5 = background.create_image(11 + (14 / 2) + (58 * c) + (2 * c),
                                                      11 + (14 / 2) + (58 * r) + (2 * r), tags=f"tile {r}-{c}",
                                                      image=black_img_75, anchor="nw")
                        animationTiles.append(ID5)

                    # update background
                    background.update()

                    # sleep
                    sleep(self.aniSpeed)

                    # remove animation tile
                    if len(animationTiles) > 0:
                        background.delete(animationTiles[-1])

                    # update background
                    background.update()

                    # animation done 100%
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        shapeID = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                          tags=f"tile {r}-{c}", image=white_img, anchor="nw")
                        self.tiles.append([shapeID, (r, c)])
                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        shapeID = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                          tags=f"tile {r}-{c}", image=black_img, anchor="nw")
                        self.tiles.append([shapeID, (r, c)])

                    # update background
                    background.update()
                # end of animation
        # animation variable is False, don't animate
        else:
            # iterate through the board_matrix
            for r in range(8):
                for c in range(8):
                    # if the tile at matrix[r][c] is white, place a white piece
                    if self.board_matrix[r][c] == "w":
                        # shapeID = background.create_image(11 + (58 * r) + (2 * r), 11 + (58 * c) + (2 * c), tags=f"tile {r}-{c}", image=white_img, anchor="nw")
                        shapeID = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                          tags=f"tile {r}-{c}", image=white_img, anchor="nw")
                        self.tiles.append([shapeID, (r, c)])

                    # if the tile at matrix[r][c] is black, place a black piece
                    elif self.board_matrix[r][c] == "b":
                        # shapeID = background.create_image(11 + (58 * r) + (2 * r), 11 + (58 * c) + (2 * c), tags=f"tile {r}-{c}", image=black_img, anchor="nw")
                        shapeID = background.create_image(11 + (58 * c) + (2 * c), 11 + (58 * r) + (2 * r),
                                                          tags=f"tile {r}-{c}", image=black_img, anchor="nw")
                        self.tiles.append([shapeID, (r, c)])

        # an if statement used to restrict the placement of green dots when playing against a computer
        # if the current player is the computer then don't place green dots
        if self.player != self.computer:
            # get the list of valid moves
            valid_moves = validMoveList(self.board_matrix, self.player)
            # for each valid move, place a green dot
            for tile in valid_moves:
                # get the tile's cords
                x = tile[0]
                y = tile[1]
                # create the green dot
                shapeID = background.create_image(11 + (58 * y) + (2 * y), 11 + (58 * x) + (2 * x), tags="green_dot",
                                                  image=green_dot_img, anchor="nw")
                # add ID to list to delete later
                self.tiles.append([shapeID, (x, y)])

        # display current player and number of pieces for each color
        self.displayBottom()

        # check if player needs to pass their turn
        self.checkPass()

        # check end game conditions and display end screen if conditions are met
        self.endGame()

    # function where the computer's move is made
    def computerMove(self):
        # rest totalStates
        self.totalStates = 0

        # get possible moves
        posMoves = validMoveList(deepcopy(self.board_matrix), self.player)

        # if there is a corner tile, take it
        if (0, 0) in posMoves:
            self.placePiece(0, 0)
            print("auto take corner")
            if not self.anime:
                sleep(self.sl)
        elif (0, 7) in posMoves:
            self.placePiece(0, 7)
            print("auto take corner")
            if not self.anime:
                sleep(self.sl)
        elif (7, 0) in posMoves:
            self.placePiece(7, 0)
            print("auto take corner")
            if not self.anime:
                sleep(self.sl)
        elif (7, 7) in posMoves:
            self.placePiece(7, 7)
            print("auto take corner")
            if not self.anime:
                sleep(self.sl)
        # if no corners are available, proceed to perform mini-max
        else:
            if self.player == 0:
                maximizer = False
                if self.debug:
                    print("Minimizing")
            else:
                maximizer = True
                if self.debug:
                    print("Maximizing")

            if not self.anime:
                # get the start time of the minimax algorithm
                start_time = time()

            # # get the result from the minimax algorithm with alpha beta pruning
            # if self.pruning:
            #     if self.debug:
            #         print("alpha beta")
            #     result = self.AlphaBeta(deepcopy(self.board_matrix), deepcopy(self.player), self.depth, -float("inf"), float("inf"), maximizer)
            # # get the result from the minimax algorithm without alpha beta pruning
            # else:
            #     result = self.MiniMax(deepcopy(self.board_matrix), deepcopy(self.player), self.depth, maximizer)

            # Mary Nations' minimax function
            self.miniMax(self.player, self.depth, deepcopy(self.board_matrix), posMoves, maximizer, -9999, 9999)

            if not self.anime:
                # get the end time of the minimax algorithm and calculate the computeTime
                computeTime = round((time() - start_time) * 100) / 100
                # use the sleep function so that the AI places a piece after 1 or more seconds
                if computeTime < self.sl:
                    sleep(self.sl - computeTime)

        # print the total number of game states examined
        print("self.totalStates = " + str(self.totalStates))

        # # get the results from the minimax algorithm
        # if len(result) == 3:
        #     # get the tile the computer wants to make a move at
        #     bestChoice = result[2]
        #     self.placePiece(bestChoice[0], bestChoice[1])
        # elif len(result) == 2:
        #     bestBoard = result[1]
        #     self.board_matrix = bestBoard
        #     self.player = 1 - self.player
        #     self.updateBoard()

    # Mary Nations' code
    # implements the Mini-Max algorithm
    def miniMax(self, player, depth, matrix, posMoves, maximizeBool, alpha, beta):
        # get the player's color (0 is white and 1 is black) and the opposing color
        color = ""
        if player == 0:
            color = "w"
        elif player == 1:
            color = "b"

        # if we have reached our depth or there are no moves to make (i.e), game over
        # return the score of the current board
        if depth == 0 or len(posMoves) == 0:
            # get the net score (black wants to maximize, and white wants to minimize),
            # so return black-white score.
            # return [heuristic(matrix, player), matrix]
            return heuristic(matrix, player)

        # maximizing loop
        if maximizeBool:
            maxEval = -9999  # represents negative infinity
            # save the 1st position in the list
            currentBestPos = posMoves[0]
            # loop through all the possible moves
            for move in posMoves:
                # count game state examined
                self.totalStates += 1
                # copy score
                # updatedScore = scoreArr[:]
                # copy the board, and add the move
                tempBoard = [row[:] for row in matrix]
                tempBoard[move[0]][move[1]] = color
                # updatedScore[playerScore] += 1
                # process flank and get new score
                # outFlank([int(move[0]), int(move[2])], player, tempBoard, updatedScore)
                # get new possible moves
                newPosMoves = validMoveList(tempBoard, 1 - player)
                nextEval = self.miniMax(1 - player, depth - 1, tempBoard, newPosMoves, False, alpha, beta)
                # save best move and update maxEval
                if nextEval > maxEval:
                    currentBestPos = move
                    maxEval = nextEval
                # update alpha
                alpha = max(alpha, nextEval)

                if self.debug:
                    print("\n\nAt ply {}".format(depth))
                    print("considering the following move:")
                    printBoard(tempBoard)
                    print("Got a heuristic score of {}".format(nextEval))
                    print("alpha = {}\tbeta = {}".format(alpha, beta))

                if self.pruning:
                    # prune
                    if beta <= alpha:
                        if self.debug:
                            print("Alpha pruned\n\n")
                        break
            # if we have exited the loop, and we are at the root of the tree
            if depth == self.depth:
                # make the best move
                self.placePiece(currentBestPos[0], currentBestPos[1])
            return maxEval

        # minimizing loop
        else:
            minEval = 9999  # represents positive infinity
            # save the 1st position in the list
            currentBestPos = posMoves[0]
            # loop through all the possible moves
            for move in posMoves:
                # count game state examined
                self.totalStates += 1
                # copy score
                # updatedScore = scoreArr[:]
                # copy the board, and add the move
                tempBoard = [row[:] for row in matrix]
                tempBoard[move[0]][move[1]] = color
                # updatedScore[playerScore] += 1
                # process flank and get new score
                # outFlank([int(move[0]), int(move[2])], player, tempBoard, updatedScore)
                # get new possible moves
                newPosMoves = validMoveList(tempBoard, 1 - player)
                nextEval = self.miniMax(1 - player, depth - 1, tempBoard, newPosMoves, True, alpha, beta)
                # save best move and update maxEval
                if nextEval < minEval:
                    currentBestPos = move
                    minEval = nextEval
                # update beta
                beta = min(beta, nextEval)

                if self.debug:
                    print("\n\nAt ply {}".format(depth))
                    print("considering the following move:")
                    printBoard(tempBoard)
                    print("Got a heuristic score of {}".format(nextEval))
                    print("alpha = {}\tbeta = {}".format(alpha, beta))

                if self.pruning:
                    # prune
                    if beta <= alpha:
                        if self.debug:
                            print("Beta pruned\n\n")
                        break
            # if we have exited the loop, and we are at the root of the tree
            if depth == self.depth:
                # make the best move
                self.placePiece(currentBestPos[0], currentBestPos[1])
            return minEval

    # minimax algorithm without alpha beta pruning
    def MiniMax(self, matrix: list, player: int, depth: int, maximizingPlayer: bool):
        # create lists to keep track of the valid moves and boards after said move
        boards = []
        choices = []

        # fill the lists with the valid moves/boards
        for x in range(8):
            for y in range(8):
                # check if this is a valid move
                if validMove(matrix, player, x, y):
                    test = getBoardAfterMove(matrix, player, x, y)
                    boards.append(test)
                    choices.append((x, y))

        # print the depth, sequences, and heuristics
        if self.debug:
            print(f"depth: {depth}")
            print("heuristic(matrix, player): " + str(heuristic(matrix, player)))
            print("matrix: ")
            for i in matrix:
                print(str(i))

        # if depth == 0 or end game condition is met
        if depth == 0 or len(choices) == 0:
            return [heuristic(matrix, player), matrix]

        # player is maximized
        if maximizingPlayer:
            maxEval = -float("inf")
            # lists to keep track of the best board and best move/choice
            bestBoard = []
            bestChoice = []
            # iterate through the children
            for brd in boards:
                boardValue = self.MiniMax(brd, 1 - player, depth - 1, False)[0]
                # maxEval = max(maxEval, eval)
                if boardValue > maxEval:
                    maxEval = boardValue
                    bestBoard = brd
                    bestChoice = choices[boards.index(brd)]
                # increment the total game states
                self.totalStates += 1
            return [maxEval, bestBoard, bestChoice]
        # player is minimized
        else:
            minEval = float("inf")
            # lists to keep track of the best board and best move/choice
            bestBoard = []
            bestChoice = []
            # iterate through the children
            for brd in boards:
                self.totalStates += 1
                boardValue = self.MiniMax(brd, 1 - player, depth - 1, True)[0]
                # minEval = min(minEval, eval)
                if boardValue < minEval:
                    minEval = boardValue
                    bestBoard = brd
                    bestChoice = choices[boards.index(brd)]
                    # increment the total game states
                self.totalStates += 1
            return [minEval, bestBoard, bestChoice]

    # minimax algorithm with alpha beta pruning
    def AlphaBeta(self, matrix: list, player: int, depth: int, alpha: float, beta: float, maximizingPlayer: bool):
        # create lists to keep track of the valid moves and boards after said move
        boards = []
        choices = []

        # fill the lists with the valid moves/boards
        for x in range(8):
            for y in range(8):
                # check if this is a valid move
                if validMove(matrix, player, x, y):
                    test = getBoardAfterMove(matrix, player, x, y)
                    boards.append(test)
                    choices.append((x, y))

        # print the depth, sequences, and heuristics
        if self.debug:
            print(f"depth: {depth}")
            print("heuristic(matrix, player): " + str(heuristic(matrix, player)))
            print("matrix: ")
            for i in matrix:
                print(str(i))

        # if depth == 0 or end game condition is met
        if depth == 0 or len(choices) == 0:
            return [heuristic(matrix, player), matrix]

        # player is maximized
        if maximizingPlayer:
            maxEval = -float("inf")
            # lists to keep track of the best board and best move/choice
            bestBoard = []
            bestChoice = []
            # iterate through the children
            for brd in boards:
                boardValue = self.AlphaBeta(brd, 1 - player, depth - 1, alpha, beta, False)[0]
                # maxEval = max(maxEval, eval)
                if boardValue > maxEval:
                    maxEval = boardValue
                    bestBoard = brd
                    bestChoice = choices[boards.index(brd)]
                alpha = max(alpha, boardValue)
                if beta <= alpha:
                    break
                # increment the total game states
                self.totalStates += 1
            return [maxEval, bestBoard, bestChoice]
        # player is minimized
        else:
            minEval = float("inf")
            # lists to keep track of the best board and best move/choice
            bestBoard = []
            bestChoice = []
            # iterate through the children
            for brd in boards:
                boardValue = self.MiniMax(brd, 1 - player, depth - 1, True)[0]
                # minEval = min(minEval, eval)
                if boardValue < minEval:
                    minEval = boardValue
                    bestBoard = brd
                    bestChoice = choices[boards.index(brd)]
                beta = min(beta, boardValue)
                if beta <= alpha:
                    break
                # increment the total game states
                self.totalStates += 1
            return [minEval, bestBoard, bestChoice]

    # function used to display/update the score board on the right side
    def displayBottom(self):
        # get rid of the score board so that we can make a new one
        self.score_board.destroy()

        # initialize counters
        white = 0
        black = 0

        # get the player's color (0 is white and 1 is black) and the opposing color
        color = ""
        if self.player == 0:
            color = "White"
        elif self.player == 1:
            color = "Black"

        # count the number of pieces for each color
        for r in range(8):
            for c in range(8):
                if self.board_matrix[r][c] == "w":
                    white += 1
                elif self.board_matrix[r][c] == "b":
                    black += 1

        # create and place the score board label
        score_text = f"{color}'s Turn\nWhite = {white}, Black = {black}"
        self.score_board = Label(root, text=score_text, font='Helvetica 25 bold')
        self.score_board.place(x=675, y=10, anchor=N)

    # function used to check if the player has to skip their turn
    def checkPass(self):
        # set pass turn to true
        self.pass_turn = True

        # get the number of empty moves and check if there are any valid moves
        empty = 0
        for r in range(8):
            for c in range(8):
                if self.board_matrix[r][c] == "e":
                    empty += 1
                valid = validMove(self.board_matrix, self.player, r, c)
                if valid:
                    self.pass_turn = False

        # if the player needs to pass their turn then swap players and update the board
        if self.pass_turn and empty > 0:
            self.player = 1 - self.player
            self.updateBoard()

    # function used to place a piece on the board, based on the othello rules
    def placePiece(self, row, col):
        # copy and add the previous board to the list
        matrix = deepcopy(self.board_matrix)
        self.prev_boards.append(matrix)
        self.prev_moves.append((row, col))

        # get the player's color (0 is white and 1 is black)
        color = ""
        if self.player == 0:
            color = "w"
        elif self.player == 1:
            color = "b"
        # check if this is a valid move
        valid = validMove(self.board_matrix, self.player, row, col)
        # if the move is valid then you place the current player's piece and flip the tiles in the flip list
        if valid:
            # place piece with the current player's color
            self.board_matrix[row][col] = color

            print(f"\n{color} made move at {row}, {col}")

            # get the neighbors of the tile at (row, col)
            neighbors = []
            for i in range(max(0, row - 1), min(row + 2, 8)):
                for j in range(max(0, col - 1), min(col + 2, 8)):
                    # if there is a non-empty space next to the attempted move then there is a neighbor
                    if self.board_matrix[i][j] != "e":
                        # add the (row, column) tuple to the neighbors list
                        neighbors.append((i, j))

            # get the tiles that you need to flip
            flip = []
            # iterate through the neighbors to see if a "row" is formed (check rules from pdf to know what a row is)
            for nei in neighbors:
                # get the neighbor's row and col from the tuple
                nei_row = nei[0]
                nei_col = nei[1]

                # if nei has the current player's color then move onto the next neighbor
                if self.board_matrix[nei_row][nei_col] == color:
                    continue
                else:
                    path = []
                    # get the direction to move in from the attempted move
                    # NW N NE       (-1, -1) (-1,  0) (-1,  1)
                    # W     E  -->  ( 0, -1) ( 0,  0) ( 0,  1)
                    # SW S SE       ( 1, -1) ( 1,  0) ( 1,  1)
                    delta_row = nei_row - row
                    delta_col = nei_col - col
                    # variables used to keep track of the current spot in the matrix
                    curr_row = nei_row
                    curr_col = nei_col

                    # while curr_row and curr_col is still in the matrix bounds
                    while 0 <= curr_row <= 7 and 0 <= curr_col <= 7:
                        # append current tile to the path
                        path.append((curr_row, curr_col))
                        # when you reach an empty space, break out of the loop since there the path has ended
                        if self.board_matrix[curr_row][curr_col] == "e":
                            break
                        # else when you reach a piece with the current player's color, copy the path list to the flip list and break out of the loop
                        elif self.board_matrix[curr_row][curr_col] == color:
                            for tile in path:
                                if tile != (curr_row, curr_col):
                                    flip.append(tile)
                            break

                        # increment the cords with the direction gotten from earlier
                        curr_row += delta_row
                        curr_col += delta_col

            # get flipped tiles to animate if anime is True
            if self.anime:
                self.flippedTiles = deepcopy(flip)

            # flip the tiles in the flip list
            for tile in flip:
                # print("flip: " + str(tile))
                self.board_matrix[tile[0]][tile[1]] = color
            # since the player made a valid move, switch players
            self.player = 1 - self.player

        # print the board
        # printBoard(self.board_matrix)

        self.updateBoard()
        background.update()

        # computer's turn to move after yours
        if self.winner == "TBD" and self.computer != -1 and self.player == self.computer:
            self.computerMove()

    # undo the last move
    def undoMove(self):
        # don't animate
        self.anime = False
        self.UNDO = True

        # don't undo the beginning board
        if len(self.prev_boards) > 0:
            # if player vs player go back one move
            if self.computer == -1:
                print("undo move: player vs player")
                # get the previous board
                previousBoard = self.prev_boards[-1]
                # previousMove = self.prev_moves[-1]
                # delete the last board in the list since it is now the current board
                del self.prev_boards[-1]
                del self.prev_moves[-1]
                # set the previous board as the current board
                self.board_matrix = previousBoard
                # change players since you are going back a move
                self.player = 1 - self.player

            # if playing against a computer then go back two moves
            elif self.computer != -1:
                print("undo move: player vs computer")
                # get the previous board
                previousBoard = self.prev_boards[-2]
                # previousMove = self.prev_moves[-2]
                # delete the last board in the list since it is now the current board
                del self.prev_boards[-1]
                del self.prev_boards[-1]
                del self.prev_moves[-1]
                del self.prev_moves[-1]
                # set the previous board as the current board
                self.board_matrix = previousBoard
                # change players since you are going back a move
                self.player = 1 - self.player
                self.player = 1 - self.player

            # update the tiles and score board
            self.updateBoard()

            # reset self.UNDO, self.anime
            self.UNDO = False
            self.anime = self.backupAnime

    # check for the end game conditions
    def endGame(self):
        end = False
        no_empty = False
        no_white = False
        no_black = False
        white = 0
        black = 0
        empty = 0

        for r in range(8):
            for c in range(8):
                if self.board_matrix[r][c] == "w":
                    white += 1
                elif self.board_matrix[r][c] == "b":
                    black += 1
                elif self.board_matrix[r][c] == "e":
                    empty += 1

        # print(f"Check End: White = {white}, Black = {black}, Empty = {empty}")

        if empty == 0:
            no_empty = True
            end = True
            print(f"no_empty = {no_empty}, end = {end}")
        if white == 0:
            no_white = True
            end = True
            print(f"no_white = {no_white}, end = {end}")
        if black == 0:
            no_black = True
            end = True
            print(f"no_black = {no_black}, end = {end}")

        if end:
            if no_black or white > black:
                self.winner = "White"
                print(f"winner = {self.winner}")
                self.endScreen(white, black)
            if no_white or black > white:
                self.winner = "Black"
                print(f"winner = {self.winner}")
                self.endScreen(white, black)
            if no_empty and white == black:
                self.winner = "Tie"
                print(f"winner = {self.winner}")
                self.endScreen(white, black)

    def endScreen(self, white, black):
        if self.winner == "White" or self.winner == "Black":
            print("End screen: White or Black")
            win_text = self.winner + f" Won\nWhite = {white}, Black = {black}"
            Label(root, text=win_text, font='Helvetica 25 bold').place(relx=.5, rely=.5, anchor=CENTER)
        elif self.winner == "Tie":
            print("End screen: Tie")
            win_text = f"Game Tied\nWhite = {white}, Black = {black}"
            Label(root, text=win_text, font='Helvetica 25 bold').place(relx=.5, rely=.5, anchor=CENTER)

    def changeAlphaBeta(self):
        if self.var1.get() == 1:
            self.pruning = True
        elif self.var1.get() == 0:
            self.pruning = False

    def changeDebug(self):
        if self.var2.get() == 1:
            self.debug = True
        elif self.var2.get() == 0:
            self.debug = False

    def changeDepth0(self):
        self.depth = 0
        print("depth set to 0")

    def changeDepth1(self):
        self.depth = 1
        print("depth set to 1")

    def changeDepth2(self):
        self.depth = 2
        print("depth set to 2")

    def changeDepth3(self):
        self.depth = 3
        print("depth set to 3")

    def changeDepth4(self):
        self.depth = 4
        print("depth set to 4")

    def changeDepth5(self):
        self.depth = 5
        print("depth set to 5")

    def changeAnime(self):
        if self.anime:
            self.anime = False
        else:
            self.anime = True
        print(f"anime set to {self.anime}")


# heuristic function to get the weighted sum of the given board (matrix)
def heuristic(matrix, player):
    # board's weighted sum
    board_value = 0
    # weights
    corner = 50
    adjacent = 5
    side = 5

    # Set player color and opponent colours
    if player == 1:
        color = "b"
        opColor = "w"
    else:
        color = "w"
        opColor = "b"

    # Go through all the tiles
    for x in range(8):
        for y in range(8):
            # Normal tiles worth 1
            value = 1

            # tiles that are adjacent to corners
            if (x == 0 and y == 1) or (x == 1 and 0 <= y <= 1):
                if matrix[0][0] == color:
                    value = side
                elif matrix[0][0] == opColor:
                    value = -adjacent
                elif matrix[0][0] == "e":
                    value = -adjacent

            elif (x == 0 and y == 6) or (x == 1 and 6 <= y <= 7):
                if matrix[7][0] == color:
                    value = side
                elif matrix[0][0] == opColor:
                    value = -adjacent
                elif matrix[0][0] == "e":
                    value = -adjacent

            elif (x == 7 and y == 1) or (x == 6 and 0 <= y <= 1):
                if matrix[0][7] == color:
                    value = side
                elif matrix[0][0] == opColor:
                    value = -adjacent
                elif matrix[0][0] == "e":
                    value = -adjacent

            elif (x == 7 and y == 6) or (x == 6 and 6 <= y <= 7):
                if matrix[7][7] == color:
                    value = side
                elif matrix[0][0] == opColor:
                    value = -adjacent
                elif matrix[0][0] == "e":
                    value = -adjacent

            # tiles that are on the edge of the board but not adjacent to a corner
            elif (x == 0 and 1 < y < 6) or (x == 7 and 1 < y < 6) or (y == 0 and 1 < x < 6) or (y == 7 and 1 < x < 6):
                value = side

            # Corner tiles
            elif (x == 0 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 0) or (x == 7 and y == 7):
                value = corner

            # Add or subtract the value of the tile corresponding to the colour
            if matrix[x][y] == color:
                board_value += value
            elif matrix[x][y] == opColor:
                board_value -= value

    return board_value


def getBoardAfterMove(board_matrix, player, row, col):
    # get a copy of the board
    matrix = deepcopy(board_matrix)

    # get the player's color (0 is white and 1 is black)
    color = ""
    opColor = ""
    if player == 0:
        color = "w"
        opColor = "b"
    elif player == 1:
        color = "b"
        opColor = "w"

    # check if this is a valid move
    valid = validMove(matrix, player, row, col)
    # if the move is valid then you place the current player's piece and flip the tiles in the flip list
    if valid:
        # place piece with the current player's color
        matrix[row][col] = color

        # get the neighbors of the tile at (row, col)
        neighbors = []
        for i in range(max(0, row - 1), min(row + 2, 8)):
            for j in range(max(0, col - 1), min(col + 2, 8)):
                # if there is a non-empty space next to the attempted move then there is a neighbor
                if matrix[i][j] != "e":
                    # add the (row, column) tuple to the neighbors list
                    neighbors.append((i, j))

        # get the tiles that you need to flip
        flip = []
        # iterate through the neighbors to see if a "row" is formed (check rules from pdf to know what a row is)
        for nei in neighbors:
            # get the neighbor's row and col from the tuple
            nei_row = nei[0]
            nei_col = nei[1]

            # if nei has the current player's color then move onto the next neighbor
            if matrix[nei_row][nei_col] == color:
                continue
            else:
                # list used to keep track of the path traversed
                path = []
                # get the direction to move in from the attempted move
                # NW N NE       (-1, -1) (-1,  0) (-1,  1)
                # W     E  -->  ( 0, -1) ( 0,  0) ( 0,  1)
                # SW S SE       ( 1, -1) ( 1,  0) ( 1,  1)
                delta_row = nei_row - row
                delta_col = nei_col - col
                # variables used to keep track of the current spot in the matrix
                curr_row = nei_row
                curr_col = nei_col

                # while curr_row and curr_col is still in the matrix bounds
                while 0 <= curr_row <= 7 and 0 <= curr_col <= 7:
                    # append current tile to the path if the tile is the opponents color
                    if matrix[curr_row][curr_col] == opColor:
                        path.append((curr_row, curr_col))
                    # when you reach an empty space, break out of the loop since the path has ended
                    elif matrix[curr_row][curr_col] == "e":
                        break
                    # else when you reach a piece with the current player's color, copy the path list to the flip list and break out of the loop
                    elif matrix[curr_row][curr_col] == color:
                        for tile in path:
                            flip.append(tile)
                        break

                    # increment the cords with the direction gotten from earlier
                    curr_row += delta_row
                    curr_col += delta_col

        # flip the tiles in the flip list
        for tile in flip:
            # print("flip: " + str(tile))
            matrix[tile[0]][tile[1]] = color

    return matrix


def validMoveList(board_matrix, player):
    # list to store all valid moves
    valid_moves = []
    # if board.debug:
    #     print(f"validMoveList: player = {player}: {type(player)}, board_matrix: ")
    #     for i in board_matrix:
    #         print(str(i))

    for x in range(8):
        for y in range(8):
            # check if this is a valid move
            valid = validMove(board_matrix, player, x, y)
            if valid:
                # if board.debug:
                #     print(f"validMoveList (valid move): player = {player}: {type(player)}, board_matrix: ")
                #     for i in board_matrix:
                #         print(str(i))
                valid_moves.append((x, y))
    # if board.debug:
    #     print("valid_moves: ")
    #     for i in valid_moves:
    #         print(str(i))
    return valid_moves


def validMove(board_matrix, player, row, col):
    # create a copy of the board matrix, so you don't accidentally change it
    matrix = deepcopy(board_matrix)
    # get the player's color (0 is white and 1 is black) and the opposing color
    color = ""
    if player == 0:
        color = "w"
    elif player == 1:
        color = "b"
    # create instance of valid to change and return
    valid = False
    # variables to keep track of the neighbors (the tiles that have a piece and are next to the empty tile)
    neighbor = False
    neighbors = []

    # if the tile you are trying to place a piece on already has a piece, then it is not a valid move
    if matrix[row][col] != "e":
        return valid
    # the tile is empty
    else:
        # A for loop to go through the tiles next to (and including) the empty space you are trying to place a piece at
        # max() and min() are used to keep the range inside the 8x8 board
        for i in range(max(0, row - 1), min(row + 2, 8)):
            for j in range(max(0, col - 1), min(col + 2, 8)):
                # if there is a non-empty space next to the attempted move then there is a neighbor
                if matrix[i][j] != "e":
                    neighbor = True
                    # add the (row, column) tuple to the neighbors list
                    neighbors.append((i, j))
        # if neighbor was not set to True in the nested for loop above
        # then there are no neighbors around the attempted move, this means the move is not valid
        if not neighbor:
            return valid
        # there is at least one neighbor
        else:
            # iterate through the neighbors to see if a "row" is formed (check rules from pdf to know what a row is)
            for nei in neighbors:
                # get the neighbor's row and col from the tuple
                nei_row = nei[0]
                nei_col = nei[1]

                # if nei has the current player's color then move onto the next neighbor
                if matrix[nei_row][nei_col] == color:
                    continue
                else:
                    # get the direction to move in from the attempted move
                    # NW N NE       (-1, -1) (-1,  0) (-1,  1)
                    # W     E  -->  ( 0, -1) ( 0,  0) ( 0,  1)
                    # SW S SE       ( 1, -1) ( 1,  0) ( 1,  1)
                    delta_row = nei_row - row
                    delta_col = nei_col - col
                    # variables used to keep track of the current spot in the matrix
                    curr_row = nei_row
                    curr_col = nei_col

                    # while curr_row and curr_col is still in the matrix bounds
                    while 0 <= curr_row <= 7 and 0 <= curr_col <= 7:
                        # when you reach an empty space, break out of the loop since there the "row" has ended
                        if matrix[curr_row][curr_col] == "e":
                            break
                        # else when you reach a piece with the current player's color, set valid to true and break out of the loop
                        elif matrix[curr_row][curr_col] == color:
                            valid = True
                            break

                        # increment the cords with the direction gotten from earlier
                        curr_row += delta_row
                        curr_col += delta_col
            # return the result
            return valid


# this functin prints the current board state
def printBoard(matrix):
    # print an index row
    print("    0  1  2  3  4  5  6  7")
    # for every row in the matrix
    for i in range(len(matrix[0])):
        # print the index columns
        print("{}  ".format(i), end='')
        # for every column in the row
        for j in range(len(matrix)):
            # print the items surrounded by spaces, and do not return
            if matrix[i][j] == "e":
                s = " "
            else:
                s = matrix[i][j]
            print(" {} ".format(s), end='')
        # return for new line
        print("")
    # print the game stats
    # print("\nPlayer Black Score: {}\tPlayer White Score: {}\n".format(scores[0], scores[1]))


def click(event):
    # get the x, y cords the mouse clicked at
    xClick = event.x
    yClick = event.y

    # iterate through the board matrix
    for row in range(8):
        for col in range(8):
            # look up what the cords are for the current tile
            xCord = tileCords[row][col][0]
            yCord = tileCords[row][col][1]
            # if the x, y cords are within the bounds of a tile, then send the row and col of that tile
            # to the placePiece function
            if xCord <= xClick <= (xCord + 58) and yCord <= yClick <= (yCord + 58):
                board.placePiece(col, row)
                # print("clicked: " + str((col, row)))


# def createBoard():

if __name__ == '__main__':
    # Tkinter setup
    root = Tk()
    root.title("Othello")
    root.geometry("850x500")

    # create a canvas so we can place/move images on it
    background = Canvas(root, width=850, height=500, background="#f0f0f0")
    background.place(x=0, y=0)

    # load and create the board
    board_img = PhotoImage(file='pictures/board_500x500.png')
    background.create_image(0, 0, tags="board_img", image=board_img, anchor="nw")

    # load the pieces and green dot images to use in the updateBoard function
    white_img = PhotoImage(file='pictures/white_piece-58x58.png')
    white_img_75 = PhotoImage(file='pictures/white_piece-58x58_75%.png')  # 44x44 (-14)
    white_img_50 = PhotoImage(file='pictures/white_piece-58x58_50%.png')  # 29x29 (-15)
    white_img_25 = PhotoImage(file='pictures/white_piece-58x58_25%.png')  # 15x15 (-14)
    black_img = PhotoImage(file='pictures/black_piece-58x58.png')
    black_img_75 = PhotoImage(file='pictures/black_piece-58x58_75%.png')
    black_img_50 = PhotoImage(file='pictures/black_piece-58x58_50%.png')
    black_img_25 = PhotoImage(file='pictures/black_piece-58x58_25%.png')
    green_dot_img = PhotoImage(file='pictures/green_dot_glow.png')

    # Create the board and update it
    board = Board()
    board.updateBoard()

    # create a list to store the cords of each tile on the board
    tileCords = [[(11 + (58 * r) + (2 * r), 11 + (58 * c) + (2 * c)) for c in range(8)] for r in range(8)]

    # bind the mouse 1 button to the background canvas widget so that whenever you click on the canvas
    # it will call the click function and send it the event object
    background.bind('<Button-1>', click)

    root.mainloop()
