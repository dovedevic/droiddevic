import datetime
import logging
import random
import math

from GameParent import Game
from GameParent import SetupFailure, SetupSuccess

logger = logging.getLogger(__name__)
handler = logging.FileHandler('../logs/{}.log'.format(str(datetime.datetime.now()).replace(' ', '_').replace(':', 'h', 1).replace(':', 'm').split('.')[0][:-2]))
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s::%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class GameObject(Game):
    """
    Implements Minesweeper
    """

    @staticmethod
    def get_game_name():
        return "Minesweeper"

    @staticmethod
    def how_to_play():
        return "RussianRoulette is a game played where on each turn the users spins a virtual chamber where 1 in 6 bullets are filled. The user fires and lives or dies. If they live, then they pass the gun to the next user. The process continues until the gun is discharged. If you invoke this game with an integer argument, that integer will determine the amount of chambers present in the gun. If you invoke this with a boolean that toggles whether or not last man standing is enabled or not."

    @staticmethod
    def get_game_short_name():
        return "MS"

    async def setup(self, args):
        logger.info('Setting up a Minesweeper game...')
        print(args)
        if len(args) != 3 or (len(args) == 1 and args[0].lower() == 'help'):
            logger.debug('Could not setup game, invalid arguments or user requested help')
            return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [board-size, amount-of-bombs]`')
        elif len(self.players) > 1:
            logger.debug('Could not setup game, user provided too many users to play')
            return SetupFailure('You can\'t play Minesweeper with other people.')
        elif type(args[1]) != int or args[1] > 9 or args[1] < 2:
            logger.debug('Could not setup game, user provided too big/small playfield')
            return SetupFailure('Board size cannot be less than 2 or greater than 9')
        elif type(args[2]) != int or args[2] < 1 or args[2] >= (args[1] ** 2):
            logger.debug('Could not setup game, user provided too many/few bombs')
            return SetupFailure('Bomb count cannot be less than 1 or greater than the size of the board.')
        logger.debug('Passed standard checks setting up turn...')

        self.__board = MineSweeperBoard(args[1], args[2]), MineSweeperBoard(args[1], args[2])
        amount = args[2]
        solved = self.__board[0]
        nbombs = 0
        while nbombs != amount:
            for x in range(len(solved.board)):
                if nbombs == amount:
                    break
                t = random.randint(0, len(solved.board) - 1)
                t2 = random.randint(0, len(solved.board) - 1)
                if math.floor(random.random() * len(solved.board)) % 2 == 0:
                    if not solved.is_mine(t, t2):
                        solved.board[t][t2] = '\N{BOMB}'
                        nbombs += 1

        for row in range(len(solved.board)):
            for col in range(len(solved.board[row])):
                if solved.is_mine(row, col):
                    continue
                solved.board[row][col] = str(solved.count_mines(row, col))

        await self.channel.send(f'{self.players[0].mention}, you are good to start! Just don\'t blow up :)')
        await self.show()
        return SetupSuccess(self)

    async def move(self, args, player):
        if len(args) != 2 or type(args[0]) != int or type(args[1]) != int:
            logger.debug("Invalid move or requested help, showing help menu...")
            await self.channel.send("**Command \'move\' Usage:** `>move [column(1-{0})] [row(1-{0})]`".format(self.__board[0].size))
            return

        y, x = args[0] - 1, args[1] - 1

        if not self.__board[0].is_valid(x, y):
            return await self.channel.send('Invalid position selected')

        if self.__board[1].board[x][y] != '\N{BLACK QUESTION MARK ORNAMENT}':
            return await self.channel.send('Position already uncovered')

        if not self.__board[0].is_mine(x, y):
            self.__board[1].board[x][y] = self.__board[0].count_mines(x, y)
            self.__board[1].moves += 1

            await self.show()

        if self.__board[0].is_mine(x, y):
            await self.channel.send(self.__board[0].parse())
            logger.debug('Clearing game...')
            await self.end_game()
            logger.debug('Player has lost, sending message')
            await self.channel.send('You blew up!')

        if self.__board[1].moves + self.__board[1].bombs == self.__board[1].size ** 2:
            await self.channel.send(self.__board[0].parse())
            logger.debug('Clearing game...')
            await self.end_game()
            logger.debug('Player has won, sending message')
            await self.channel.send('You won! Congratulations!')

    async def show(self):
        board = self.__board[1].parse()
        await self.channel.send(board)


class MineSweeperBoard:
    def __init__(self, size: int, bombs: int):
        self.board = []
        for nrow in range(size):
            row = nrow
            self.board.append([])
            for ncol in range(size):
                self.board[row].append('\N{BLACK QUESTION MARK ORNAMENT}')
        self.size = size
        self.bombs = int(bombs)
        self.moves = 0

    def parse(self):
        ret = ''
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                ret += self.board[row][col]
            ret += '\n'
        return ret

    def is_mine(self, row, col):
        return self.board[row][col] == '\N{BOMB}'

    def is_valid(self, row, col):
        return (row >= 0) and (row < self.size) and (col >= 0) and (col < self.size)

    def count_mines(self, row, col):
        count = 0

        # Up
        if self.is_valid(row - 1, col):
            if self.is_mine(row - 1, col):
                count += 1

        # Down
        if self.is_valid(row + 1, col):
            if self.is_mine(row + 1, col):
                count += 1

        # Right
        if self.is_valid(row, col + 1):
            if self.is_mine(row, col + 1):
                count += 1

        # Left
        if self.is_valid(row, col - 1):
            if self.is_mine(row, col - 1):
                count += 1

        # Top Right
        if self.is_valid(row - 1, col + 1):
            if self.is_mine(row - 1, col + 1):
                count += 1

        # Top Left
        if self.is_valid(row - 1, col - 1):
            if self.is_mine(row - 1, col - 1):
                count += 1

        # Bottom Right
        if self.is_valid(row + 1, col + 1):
            if self.is_mine(row + 1, col + 1):
                count += 1

        # Bottom Left
        if self.is_valid(row + 1, col - 1):
            if self.is_mine(row + 1, col - 1):
                count += 1

        if self.is_valid(row, col):
            if self.is_mine(row, col):
                return

        nums = {'0': ':zero:', '1': ':one:', '2': ':two:',
         '3': ':three:', '4': ':four:', '5': ':five:',
         '6': ':six:', '7': ':seven:', '8': ':eight:'}

        return nums.get(str(count))
