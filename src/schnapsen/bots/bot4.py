from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GamePhase, GameState, GamePlayEngine
import random

from .rdeep import RdeepBot
from .alphabeta import AlphaBetaBot

class Bot4(Bot):
    """
    Heuristic bot tackling trump exchange in phase 1 (otherwise resort to rdeep in phase 1) and alpha-beta pruning in phase 2
    Perform trump exchange if the open trump card is a ten or an ace, or if exchanging completes a marriage.
    (Gain access to valuable cards that allow you to score more points)
    """
    def __init__(self, num_samples: int, depth: int, rand: random.Random, name: Optional[str] = None) -> None:
        """
        Create a new Bot4 bot.

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
        if perspective.get_phase() == GamePhase.ONE:
            valid_moves = [move for move in perspective.valid_moves()]
            trump_exchange = None
            has_trump_queen = False
            has_trump_king = False

            for move in valid_moves:
                if move.is_trump_exchange():
                    trump_exchange = move
                if str(move.cards[0].rank) == "KING" and str(move.cards[0].suit) == str(perspective.get_trump_suit()):
                    has_trump_king = True
                if str(move.cards[0].rank) == "QUEEN" and str(move.cards[0].suit) == str(perspective.get_trump_suit()):
                    has_trump_queen = True

            if perspective.am_i_leader() and trump_exchange != None:
                if str(perspective.get_trump_card().rank) in ["ACE", "TEN"] or (str(perspective.get_trump_card().rank) in ["KING", "QUEEN"] and (has_trump_queen or has_trump_king)):
                    return trump_exchange

            return self.delegate_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
