import datetime
import logging
import random

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
    Implements Russian Roulette
    """

    @staticmethod
    def get_game_name():
        return "RussianRoulette"

    @staticmethod
    def how_to_play():
        return "RussianRoulette is a game played where on each turn the users spins a virtual chamber where 1 in 6 bullets are filled. The user fires and lives or dies. If they live, then they pass the gun to the next user. The process continues until the gun is discharged. If you invoke this game with an integer argument, that integer will determine the amount of chambers present in the gun. If you invoke this with a boolean that toggles whether or not last man standing is enabled or not."

    @staticmethod
    def get_game_short_name():
        return "RR"

    async def setup(self, args):
        self.__shots = 0
        self.__gun = 6
        self.__last_man_standing = True
        self.__current_turn_index = 0

        logger.info('Setting up a RussianRoulette game...')
        if len(args) == 2:
            if (type(args[0]) == bool and type(args[1]) == int) or (type(args[0]) == int and type(args[1]) == bool):
                if type(args[0]) == bool:
                    self.__last_man_standing = args[0]
                else:
                    self.__gun = args[0]
                if type(args[1]) == bool:
                    self.__last_man_standing = args[1]
                else:
                    self.__gun = args[1]
            else:
                logger.debug('Could not setup game, invalid arguments')
                return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [users-to-play, ...] (number_of_empty_chambers=5 (int)) (last_man_standing=false (boolean))`')
        elif len(args) == 1:
            if type(args[0]) == bool or type(args) == int:
                if type(args[0]) == bool:
                    self.__last_man_standing = args[0]
                else:
                    self.__gun = args[0]
            else:
                logger.debug('Could not setup game, invalid arguments')
                return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [users-to-play, ...] (number_of_empty_chambers=5 (int)) (last_man_standing=false (boolean))`')
        elif len(args) > 0 and (len(args) == 1 and args[0].lower() == 'help'):
            logger.debug('Could not setup game, invalid arguments or user requested help')
            return SetupFailure(f'**Command \'play {self.get_game_short_name()}\' Usage: **`>play {self.get_game_short_name()} [users-to-play, ...] (number_of_empty_chambers=5) (last_man_standing=False)`')
        elif len(self.players) < 2:
            logger.debug('Could not setup game, user provided too few users to play')
            return SetupFailure('You can\'t play RussianRoulette by yourself.')
        if self.__gun < 1 or self.__gun > 1000:
            logger.debug('Could not setup game, user provided too big playfield')
            return SetupFailure('Invalid gun size.')
        logger.debug('Passed standard checks setting up turn...')
        random.shuffle(self.players)
        self.__current_turn_index = 0
        await self.channel.send("Playing with a gun with {} chambers, {}.".format(self.__gun, "last man standing" if self.__last_man_standing else "one bullet"))


        pidx = 0
        for player in self.players:
            if pidx == self.__current_turn_index:
                await self.channel.send("<@{0}>, you go first! Good luck!".format(player.id))
            else:
                await self.channel.send("<@{0}>, let\'s see what happens...".format(player.id))
            pidx += 1

        await self.show()
        return SetupSuccess(self)

    async def move(self, args, player):
        logger.debug('Checking turn...')
        if player != self.players[self.__current_turn_index]:
            await self.channel.send('It is not your turn currently.')
            return
        self.__shots += 1
        logger.debug("Getting number...")
        if random.randint(1, self.__gun) == self.__gun // 2:
            logger.debug("Will be a kill shot, sending message")
            # Oh no!
            await self.channel.send("**{0}**  :skull::boom::gun:".format(self.get_current_player().name))
            if not self.__last_man_standing:
                logger.debug("Clearing game...")
                await self.end_game()
                logger.debug("Sending meta-data...")
                await self.channel.send("**{0}** looses! It took {1} shots!".format(self.get_current_player().name, self.__shots))
            else:
                logger.debug("removing player and updating index")
                self.players.remove(player)

                if len(self.players) == 1:
                    logger.debug("Clearing game...")
                    await self.end_game()
                    logger.debug("Sending meta-data...")
                    await self.channel.send("**{0}** wins! It took {1} shots!".format(self.players[0].name, self.__shots))
                else:
                    self.__current_turn_index = (self.__current_turn_index - 1) % len(self.players)
                    logger.debug("Calling next turn...")
                    self.next_turn()
                    logger.debug("Showing board...")
                    await self.show()
        else:
            logger.debug("Shot not lethal, click! Sending message")
            await self.channel.send("**{0}**  :sunglasses::gun: *click*".format(self.get_current_player().name))
            logger.debug("Calling next turn...")
            self.next_turn()
            logger.debug("Showing board...")
            await self.show()

    def next_turn(self):
        self.__current_turn_index = (self.__current_turn_index + 1) % len(self.players)

    def get_current_player(self):
        return self.players[self.__current_turn_index]

    async def show(self):
        board = "**{0}**  :triumph::gun:".format(self.get_current_player().name)
        await self.channel.send(board)
