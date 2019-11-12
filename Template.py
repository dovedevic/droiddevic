import datetime
import logging

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
    Every game must have the same class name, GameObject. Do not change the name or inheritance unless it extends a
    Game object somewhere in the chain. As a GameObject...

    ** You have access to the following properties and methods:
        - self.players          ||  Property: Return a list of discord.Member or discord.User objects that subscribed to the game
        - self.bot              ||  Property: Return the discord.Bot object for getting user info or other discord details
        - self.channel          ||  Property: Return the discord.Channel object for sending messages
        - await self.end_game() ||  Method:   Notify the ending of this game

    ** You MUST implement the following definitions:
        - def get_game_name(self)        ||  Return the name of the game (@staticmethod)
        - def get_game_short_name(self)  ||  Return the shortened (2/3 letters) name of the game (@staticmethod)
        - async def setup(self, args)    ||  Setup your game however you want. `args` will be a formatted array of integers, floats, bools, or strings
        - async def move(self, args)     ||  Progress your game by one step, whatever that means for your game. `args` will be a formatted array of integers, floats, bools, or strings
        - def get_current_player(self)   ||  Return the discord.Member or discord.User of who is allowed to play currently
        - async def show(self)           ||  Show the current state of your game. Must be under 2000 characters

    ** You MAY implement the following definitions:
        - async def handle_user_leave(self, channel, player) || Handle when a user tries to resign the current game. If this is not overridden or handled, the game will end for everyone.
    """

    # TODO: Define local variables for this game
    # ...
    @staticmethod
    def get_game_name():
        return "Some Game"

    @staticmethod
    def how_to_play():
        return "Game rules"

    @staticmethod
    def get_game_short_name():
        return "SG"

    async def setup(self, args):
        if len(self.players) == 1:
            pass  # Singleplayer
        else:
            pass  # Multiplayer

        if len(args) == 0:
            pass  # No args were given
        else:
            if isinstance(args[0], int):  # Is the first arg an int?
                pass
            # ...

        if True:  # Some game conditions were met...
            # Setup who's turn it is
            # Show the initial state of the game
            await self.show()
            # Tell the game manager the setup was a success
            return SetupSuccess(self)
        else:  # Some game conditions were not met, thus the game cannot be setup...
            return SetupFailure("The game can not be setup because of some default reason!")

    async def move(self, args):
        # TODO: Define some game logic
        # ...
        # TODO: Update whos turn it is
        # ...
        # Show the state of the game after a move is performed, typically
        await self.show()

    def get_current_player(self):
        # TODO: Define some logic for getting the current player
        return self.players[0]  # For now, only the first player is allowed to make moves

    async def show(self):
        # TODO: Define some logic for transforming your game to a string
        board = "<some game state for formatted string here>"
        # Send the state of the game to the channel where the game is being hosted
        await self.channel.send(board)

    # Not implemented, allowing game to end for all when a resign occurs. Change this if you allow users to resign mid-game
    # async def handle_user_leave(self, channel, player):
    #    pass
