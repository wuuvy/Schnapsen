"""Create a bot in a separate .py and import them here, so that one can simply import
it by from schnapsen.bots import MyBot.
"""
from .rand import RandBot
from .alphabeta import AlphaBetaBot
from .rdeep import RdeepBot
from .ml_bot import MLDataBot, MLPlayingBot, train_ML_model
from .gui.guibot import SchnapsenServer
from .minimax import MiniMaxBot
from .bully_bot import BullyBot
from .rdeepalphabeta import RdeepAlphaBeta
from .bot1 import Bot1
from .bot2 import Bot2
from .bot3 import Bot3
from .bot4 import Bot4
from .bot5 import Bot5
from .combined_heuristics_bot import CombinedHeuristicsBot

__all__ = ["RandBot", "AlphaBetaBot", "RdeepBot", "MLDataBot", "MLPlayingBot", "train_ML_model", "SchnapsenServer", "MiniMaxBot", "BullyBot", "RdeepAlphaBeta", "Bot1", "Bot2", "Bot3", "Bot4", "Bot5", "CombinedHeuristicsBot"]
