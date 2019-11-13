import datetime
import logging
import random
import re

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
    Implements Tic-Tac-Toe
    """

    @staticmethod
    def get_game_name():
        return "TicTacToe"

    @staticmethod
    def how_to_play():
        return "TicTacToe is a game played on a 3x3 grid. Each player gets an X or O token to place on a free square. The first player to get three of their tokens in a horizontal, diagonal, or vertical section wins the game. If all cells are filled the game is a draw."

    @staticmethod
    def get_game_short_name():
        return "TTTT"

    async def setup(self, args):
        self.__board = [['⬛', '⬛', '⬛'], ['⬛', '⬛', '⬛'], ['⬛', '⬛', '⬛']]
        self.__p1 = '❌'
        self.__p2 = '⭕'
        self.__turns = 0
        self.__turn = 0

        logger.info('Setting up a TicTacToe game...')
        if len(args) > 0 or (len(args) == 1 and args[0].lower() == 'help'):
            logger.debug('Could not setup game, invalid arguments or user requested help')
            return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [users-to-play, ...]`')
        elif len(self.players) > 2:
            logger.debug('Could not setup game, user provided too many users to play')
            return SetupFailure('Why are you trying to play TicTacToe with more than 1 person? That\'s not how this works...')
        elif len(self.players) < 2:
            logger.debug('Could not setup game, user provided too few users to play')
            return SetupFailure('You can\'t play TicTacToe by yourself.')
        logger.debug('Passed standard checks setting up turn...')
        self.__turn = random.randint(0, 1)
        await self.show()

        pidx = 0
        for player in self.players:
            if pidx == self.__turn:
                await self.channel.send(f'{player.mention}, you go first! Good luck!')
            else:
                await self.channel.send(f'{player.mention}, waiting for your turn...')
            pidx += 1

        return SetupSuccess(self)

    async def move(self, args):
        logger.debug('Checking arguments...')
        if len(args) != 2:
            await self.channel.send('You need to specify a valid position on the board. `>move [col] [row]`')
        elif not args[0].isdigit() or not args[1].isdigit():
            await self.channel.send('Invalid position. Both arguments need to be numbers')
        elif int(args[0]) < 0 or int(args[0]) > 3 or int(args[1]) < 0 or int(args[1]) > 3:
            await self.channel.send('You need to specify a valid position on the board.')
        elif self.__board[int(args[1]) - 1][int(args[0]) - 1] != '⬛':
            await self.channel.send('That position is not empty. Please choose an empty spot.')
        else:
            logger.debug('Setting position on board')
            self.__board[int(args[1]) - 1][int(args[0]) - 1] = self.get_user_icon()
            self.__turns += 1
            """
            First 3 checks: Horizontal Axis
            Second 3 checks: Vertical Axis
            Last 2 checks: Diagonal Axis
            """
            if self.__board[0][0] == '❌' and self.__board[0][1] == '❌' and self.__board[0][2] == '❌' or \
               self.__board[1][0] == '❌' and self.__board[1][1] == '❌' and self.__board[1][2] == '❌' or \
               self.__board[2][0] == '❌' and self.__board[2][1] == '❌' and self.__board[2][2] == '❌' or \
               self.__board[0][0] == '❌' and self.__board[1][0] == '❌' and self.__board[2][0] == '❌' or \
               self.__board[0][1] == '❌' and self.__board[1][1] == '❌' and self.__board[2][1] == '❌' or \
               self.__board[0][2] == '❌' and self.__board[1][2] == '❌' and self.__board[2][2] == '❌' or \
               self.__board[0][0] == '❌' and self.__board[1][1] == '❌' and self.__board[2][2] == '❌' or \
               self.__board[0][2] == '❌' and self.__board[1][1] == '❌' and self.__board[2][0] == '❌':
                await self.show()
                logger.debug('Clearing game...')
                await self.end_game()
                logger.debug('Player 1 has won the game, sending message...')
                await self.channel.send(f'**{self.get_current_player().name}** wins!')
            elif self.__board[0][0] == '⭕' and self.__board[0][1] == '⭕' and self.__board[0][2] == '⭕' or \
                 self.__board[1][0] == '⭕' and self.__board[1][1] == '⭕' and self.__board[1][2] == '⭕' or \
                 self.__board[2][0] == '⭕' and self.__board[2][1] == '⭕' and self.__board[2][2] == '⭕' or \
                 self.__board[0][0] == '⭕' and self.__board[1][0] == '⭕' and self.__board[2][0] == '⭕' or \
                 self.__board[0][1] == '⭕' and self.__board[1][1] == '⭕' and self.__board[2][1] == '⭕' or \
                 self.__board[0][2] == '⭕' and self.__board[1][2] == '⭕' and self.__board[2][2] == '⭕' or \
                 self.__board[0][0] == '⭕' and self.__board[1][1] == '⭕' and self.__board[2][2] == '⭕' or \
                 self.__board[0][2] == '⭕' and self.__board[1][1] == '⭕' and self.__board[2][0] == '⭕':
                await self.show()
                logger.debug('Clearing game...')
                await self.end_game()
                logger.debug('Player 2 has won the game, sending message...')
                await self.channel.send(f'**{self.get_current_player().name}** wins!')
            else:
                logger.debug('User moved')
                if self.__turns != 9:
                    logger.debug('Calling next turn...')
                    self.next_turn()
                    await self.show()
                else:
                    logger.debug('Clearing game...')
                    await self.show()
                    await self.end_game()
                    await self.channel.send('It\'s a draw!')

    def next_turn(self):
        self.__turn = (self.__turn + 1) % 2

    def get_user_icon(self):
        if self.__turn == 0:
            return self.__p1
        else:
            return self.__p2

    def get_current_player(self):
        return self.players[self.__turn]

    async def show(self):
        board = f'{"".join(self.__board[0])}\n{"".join(self.__board[1])}\n{"".join(self.__board[2])}'
        await self.channel.send(board)
