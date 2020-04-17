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
    Implements Gomoku
    """

    @staticmethod
    def get_game_name():
        return "Gomoku"

    @staticmethod
    def how_to_play():
        return "Gomoku is a game where you place tokens on a 10 by 10 grid. The purpose of the game is to get five of your tokens in a row diagonally, horizontally, or vertically. If provided, each player can customize their token to one of the following: blue, red, brown, green, yellow, purple, yellow, white. "

    @staticmethod
    def get_game_short_name():
        return "GU"

    async def setup(self, args):
        self.__moves = 0
        self.__board = """
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
:black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle::black_circle:
    """
        self.__current_turn_index = 0
        self._tokens = {
            "blue": ":blue_circle:",
            "red": ":red_circle:",
            "green": ":green_circle:",
            "orange": ":orange_circle:",
            "purple": ":purple_circle:",
            "yellow": ":yellow_circle:",
            "white": ":white_circle:",
            "brown": ":brown_circle:",
        }
        self._player_tokens = []

        logger.info('Setting up a Gomoku game...')

        if len(args) == 1 and args[0].lower() == 'help':
            logger.debug('Could not setup game, invalid arguments or user requested help')
            return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [users-to-play] (tokens-colors-player)`')
        elif len(self.players) < 2:
            logger.debug('Could not setup game, user provided too few users to play')
            return SetupFailure('You can\'t play Gomoku by yourself.')
        elif len(args) == len(self.players) and all(type(arg) == str and arg in self._tokens for arg in args):
            for arg in args:
                self._player_tokens.append(self._tokens[arg])
        elif len(args) == 0:
            self._player_tokens = [self._tokens[k] for k in self._tokens][:len(self.players)]
        else:
            logger.debug('Could not setup game, invalid arguments or user requested help')
            return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [users-to-play] (tokens-colors-player)`')

        logger.debug('Passed standard checks setting up turn...')

        c = list(zip(self.players, self._player_tokens))
        random.shuffle(c)
        self.players, self._player_tokens = zip(*c)
        self.players = list(self.players)
        self._player_tokens = list(self._player_tokens)

        self.__current_turn_index = 0
        await self.show()

        pidx = 0
        for player in self.players:
            if pidx == self.__current_turn_index:
                await self.channel.send(f'{player.mention} your token is {self._player_tokens[pidx]}, you go first! Good luck!')
            else:
                await self.channel.send(f'{player.mention} your token is {self._player_tokens[pidx]}, waiting for your turn...')
            pidx += 1

        return SetupSuccess(self)

    async def move(self, args, player):
        logger.debug("Checking command move")
        if player != self.players[self.__current_turn_index]:
            await self.channel.send('It is not your turn currently.')
            return
        if not args or len(args) <= 1 or type(args[0]) != int or type(args[1]) != int or args[0] > 10 or args[0] < 1 or args[1] > 10 or args[1] < 1:
            logger.debug("Invalid move or requested help, showing help menu...")
            await self.channel.send("**Command \'move\' Usage:** `>move [column(1-10)] [row(1-10)]`")
            return
        logger.debug("Checking if place is appropriate")
        if self._get_item_at(args[0] - 1, args[1] - 1) != ':black_circle:':
            logger.debug("Invalid move, column full")
            await self.channel.send("You can't put a piece in that spot, try somewhere else!")
            return
        logger.debug("Placing...")
        self._place_item_at(args[0] - 1, args[1] - 1, self._player_tokens[self.__current_turn_index])
        # Check for ending
        logger.debug("Placed, checking for next turn...")
        self.__moves += 1
        if self._contains_connect_five():
            logger.debug("Showing board...")
            await self.show()
            logger.debug("Placed piece resulted in a connect five!")
            await self.channel.send("**{0}** wins! It took {1} turns!".format(self.players[self.__current_turn_index].name, self.__moves))
            logger.debug("Clearing game...")
            await self.end_game()
        else:
            logger.debug("Going to next turn...")
            self.next_turn()
            logger.debug("Showing board...")
            await self.show()

    def next_turn(self):
        self.__current_turn_index = (self.__current_turn_index + 1) % len(self.players)

    def get_current_player(self):
        return self.players[self.__current_turn_index]

    async def show(self):
        await self.channel.send("It's **{}'s** turn.".format(self.players[self.__current_turn_index].name) + self.__board)

    def _contains_connect_five(self):
        checker = self._player_tokens[self.__current_turn_index]
        # Horizontal Check
        for j in range(0, 10 - 4):
            for i in range(0, 10):
                if self._get_item_at(i, j) == checker and \
                  self._get_item_at(i, j + 1) == checker and \
                  self._get_item_at(i, j + 2) == checker and \
                  self._get_item_at(i, j + 3) == checker and \
                  self._get_item_at(i, j + 4) == checker:
                    logger.info("Found win! Placing win pieces!")
                    self._place_item_at(i, j, ':large_orange_diamond:')
                    self._place_item_at(i, j + 1, ':large_orange_diamond:')
                    self._place_item_at(i, j + 2, ':large_orange_diamond:')
                    self._place_item_at(i, j + 3, ':large_orange_diamond:')
                    self._place_item_at(i, j + 4, ':large_orange_diamond:')
                    return True
        # Vertical Check
        for i in range(0, 10 - 3):
            for j in range(0, 10):
                if self._get_item_at(i, j) == checker and \
                  self._get_item_at(i + 1, j) == checker and \
                  self._get_item_at(i + 2, j) == checker and \
                  self._get_item_at(i + 3, j) == checker and \
                  self._get_item_at(i + 4, j) == checker:
                    logger.info("Found win! Placing win pieces!")
                    self._place_item_at(i, j, ':large_orange_diamond:')
                    self._place_item_at(i + 1, j, ':large_orange_diamond:')
                    self._place_item_at(i + 2, j, ':large_orange_diamond:')
                    self._place_item_at(i + 3, j, ':large_orange_diamond:')
                    self._place_item_at(i + 4, j, ':large_orange_diamond:')
                    return True
        # Ascending Diagonal Check
        for i in range(4, 10):
            for j in range(0, 10 - 4):
                if self._get_item_at(i, j) == checker and \
                  self._get_item_at(i - 1, j + 1) == checker and \
                  self._get_item_at(i - 2, j + 2) == checker and \
                  self._get_item_at(i - 3, j + 3) == checker and \
                  self._get_item_at(i - 4, j + 4) == checker:
                    logger.info("Found win! Placing win pieces!")
                    self._place_item_at(i, j, ':large_orange_diamond:')
                    self._place_item_at(i - 1, j + 1, ':large_orange_diamond:')
                    self._place_item_at(i - 2, j + 2, ':large_orange_diamond:')
                    self._place_item_at(i - 3, j + 3, ':large_orange_diamond:')
                    self._place_item_at(i - 4, j + 4, ':large_orange_diamond:')
                    return True
        # Ascending Diagonal Check
        for i in range(4, 10):
            for j in range(4, 10):
                if self._get_item_at(i, j) == checker and \
                  self._get_item_at(i - 1, j - 1) == checker and \
                  self._get_item_at(i - 2, j - 2) == checker and \
                  self._get_item_at(i - 3, j - 3) == checker and \
                  self._get_item_at(i - 4, j - 4) == checker:
                    logger.info("Found win! Placing win pieces!")
                    self._place_item_at(i, j, ':large_orange_diamond:')
                    self._place_item_at(i - 1, j - 1, ':large_orange_diamond:')
                    self._place_item_at(i - 2, j - 2, ':large_orange_diamond:')
                    self._place_item_at(i - 3, j - 3, ':large_orange_diamond:')
                    self._place_item_at(i - 4, j - 4, ':large_orange_diamond:')
                    return True
        return False

    def _get_item_at(self, col, row):
        for idx, emoji in enumerate(re.compile(r':[a-zA-Z0-9_]+:').finditer(self.__board)):
            if idx % 10 == col:
                if idx // 10 == row:
                    return emoji.group()

    def _place_item_at(self, col, row, placer):
        for idx, emoji in enumerate(re.compile(r':[a-zA-Z0-9_]+:').finditer(self.__board)):
            if idx % 10 == col:
                if idx // 10 == row:
                    self.__board = self.__board[:emoji.start()] + placer + self.__board[emoji.end():]
                    return
