import datetime
import logging
import random
import re

from GenericUtility import Language
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
    Implements Word Play
    """

    @staticmethod
    def get_game_name():
        return "WordPlay"

    @staticmethod
    def how_to_play():
        return "WordPlay is a game where you change some feature of a word in the Oxford dictionary. Each word play must either reorder the letters, insert a letter, or remove a letter; only one transformation is allowed. For example, proper word plays on the word **car** can be cat, bar, and care. Improper word plays are race, cares, and are."

    @staticmethod
    def get_game_short_name():
        return "WP"

    async def setup(self, args):
        self.__words = []
        self.__word_list = set(word.strip().lower() for word in Language.dictionary.split('\n'))
        self.__current_turn_index = 0

        logger.info('Setting up a TicTacToe game...')
        if len(args) != 0 or (len(args) == 1 and args[0].lower() == 'help'):
            logger.debug('Could not setup game, invalid arguments or user requested help')
            return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [user-to-play]`')
        elif len(self.players) < 2:
            logger.debug('Could not setup game, user provided too few users to play')
            return SetupFailure('You must play with at least one opponent.')
        logger.debug('Passed standard checks setting up turn...')
        random.shuffle(self.players)
        self.__current_turn_index = 0
        await self.show()

        pidx = 0
        for player in self.players:
            if pidx == self.__current_turn_index:
                await self.channel.send(f'{player.mention}, you\'ll go first! Give us a word to play!')
            else:
                await self.channel.send(f'{player.mention}, please wait for the first word.')
            pidx += 1

        return SetupSuccess(self)

    async def move(self, args, player):
        logger.debug("Checking command move")
        if player != self.players[self.__current_turn_index]:
            await self.channel.send('It is not your turn currently.')
            return
        if len(args) == 0 or len(args) > 1 or args[0] == "help" or type(args[0]) != str:
            logger.debug("Invalid move or requested help, showing help menu...")
            await self.channel.send("**Command \'move\' Usage:** `>move [word]`")
            return

        submitted_word = args[0]
        logger.debug("Got word \'{}\'".format(submitted_word))
        if not self.__words:
            logger.debug("This is the first word. Setting...")
            self.__words.append(submitted_word)
            logger.debug("User has set the starting word!")
            await self.channel.send("Okay everyone, let's word play ***{0}***".format(self.__words[-1]))
            logger.debug("Calling next turn...")
            self.next_turn()
            logger.debug("Showing board...")
            await self.show()
        else:
            logger.debug("Checking word...")
            if submitted_word in self.__words:
                logger.debug("Word has been used, asking for another word...")
                await self.channel.send("That word has been used already! Give me another.")
            elif submitted_word not in self.__word_list:
                logger.debug("Word is not in the dictionary... let them retry")
                await self.channel.send("That word is not in my dictionary! Try another.")
            elif self._is_rearange(self.__words[-1], submitted_word) or self._is_valid_play(self.__words[-1], submitted_word):
                self.__words.append(submitted_word)
                logger.debug("Word is good, the words are...")
                logger.debug(str(self.__words))
                logger.debug("calling next turn...")
                self.next_turn()
                logger.debug("Showing board...")
                await self.show()
            else:
                logger.debug("Word is not good, ending game...")
                await self.channel.send("**{0}**  :face_palm: That is not a shuffle of letters or contains more than one change!".format(self.get_current_player().name))
                logger.debug("Clearing game...")
                await self.end_game()
                logger.debug("Sending meta-data...")
                if len(self.__words) > 1:
                    await self.channel.send("**{0}** loses! {1} words were played! You started with {2} and ended at {3}".format(self.get_current_player().name, len(self.__words), self.__words[0], self.__words[-1]))
                else:
                    await self.channel.send("**{0}** loses! {1} words were played!".format(self.get_current_player().name, len(self.__words)))

    def next_turn(self):
        self.__current_turn_index = (self.__current_turn_index + 1) % len(self.players)

    def get_current_player(self):
        return self.players[self.__current_turn_index]

    async def show(self):
        if not self.__words:
            await self.channel.send("**{0}** give me any word!".format(self.get_current_player().name))
        else:
            await self.channel.send("**{0}**, word play **{1}**".format(self.get_current_player().name, self.__words[-1]))

    def _is_rearange(self, word1, word2):
        if len(word1) == len(word2):
            for letter in word1:
                if letter in word2:
                    word2 = word2.replace(letter, '', 1)
                else:
                    return False
            if len(word2) == 0:
                return True
            else:
                return False
        else:
            return False

    def _is_valid_play(self, word1, word2):
        allowances = 1
        if abs(len(word1) - len(word2)) <= allowances:
            for i in range(min(len(word1), len(word2))):
                if word1[i] != word2[i]:
                    allowances -= 1
                    if allowances < 0:
                        return False
                    if len(word1) > len(word2):
                        word1 = word1[:i] + word1[i+1:]
                        if word1[i] != word2[i]:
                            print(word1, word2, i)
                            allowances -= 1
                    elif len(word1) < len(word2):
                        word2 = word2[:i] + word2[i+1:]
                        if word1[i] != word2[i]:
                            allowances -= 1
                    else:
                        pass
                    if allowances < 0:
                        return False
            return True
        else:
            return False
