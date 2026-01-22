from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GamePhase, GameState, GamePlayEngine
import random

from .rdeep import RdeepBot
from .alphabeta import AlphaBetaBot

class Bot2(Bot):
    """
    If you can play a marriage and can follow up with a different trump card/an ace, or the marriage is trump,
    play a marriage (marriages score a lot of points and being able to follow up allows you to control the tempo)
    Otherwise use rdeep.
    Use alpha-beta pruning in phase 2
    """
    def __init__(self, num_samples: int, depth: int, rand: random.Random, name: Optional[str] = None) -> None:
        """
        Create a new Bot2 bot.

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
            trump = perspective.get_trump_suit()
            for move in valid_moves:
                if move.is_marriage():
                    trump_marriage = str(move.king_card.suit) == str(trump)
                    hand = perspective.get_hand().get_cards()
                    has_followup = any(
                        str(card.rank) == "ACE" or (str(card.suit) == str(trump) and str(card.rank) in ["KING", "TEN", "ACE"])
                        for card in hand
                    )
                    if trump_marriage or has_followup:
                        return move

            return self.delegate_phase1.get_move(perspective, leader_move)
        
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
