from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GamePhase, GameState, GamePlayEngine
import random

from .rdeep import RdeepBot
from .alphabeta import AlphaBetaBot

class RdeepAlphaBeta(Bot):
    """
    A bot using rdeep in the first phase and the alpha-beta pruning strategy in the second phase of the game.
    """
    def __init__(self, num_samples: int, depth: int, rand: random.Random, name: Optional[str] = None) -> None:
        """
        Create a new rdeep alpha-beta bot.

        :param num_samples: how many samples to take per move
        :param depth: how deep to sample
        :param rand: the source of randomness for this Bot
        :param name: the name of this Bot
        """
        super().__init__(name)
        assert num_samples >= 1, f"we cannot work with less than one sample, got {num_samples}"
        assert depth >= 1, f"it does not make sense to use a dept <1. got {depth}"
        self.__num_samples = num_samples
        self.__depth = depth
        self.__rand = rand
        self.delegate_phase1 = RdeepBot(num_samples=num_samples, depth=depth, rand=rand)
        self.delegate_phase2 = AlphaBetaBot()


    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
        get_move is a function that returns the move to be played.
        In phase 1:
            Rdeep bot
        In phase 2:
            Alpha-Beta bot

        :param perspective: The perspective from which we want to decide what move to play (PlayerPerspective to prevent accessing info that the bot can not)
        :param leader_move: Optional variable that takes a Move value (the move played by the leader) when the bot is following a trick
        :return: The move to be played by the bot
        """
        if perspective.get_phase() == GamePhase.ONE:
            return self.delegate_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
