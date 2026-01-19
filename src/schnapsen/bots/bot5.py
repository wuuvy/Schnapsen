from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GamePhase, GameState, GamePlayEngine
import random

from .rdeep import RdeepBot
from .alphabeta import AlphaBetaBot

class Bot5(Bot):
    """
    Heuristic bot tackling phase 1 (resort to rdeep in phase 1 if unable to come up with move) and alpha-beta pruning in phase 2
    When there are two or less cards remaining in the talon and you are following, play to ensure you lead the next trick, if possible.
    (In phase two, leading is very important so ensuring you have the lead should lead to many advantages)
    """
    def __init__(self, num_samples: int, depth: int, rand: random.Random, name: Optional[str] = None) -> None:
        """
        Create a new Bot5 bot.

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
            if perspective.get_talon_size() <= 2:
                valid_moves = [move.as_regular_move() for move in perspective.valid_moves() if move.is_regular_move()]

                if not perspective.am_i_leader():
                    rank_values = {"JACK" : 2, "QUEEN" : 3, "KING" : 4, "TEN" : 10, "ACE" : 11}

                    for move in valid_moves:    
                        if str(leader_move.cards[0].suit) != str(perspective.get_trump_suit()):
                            if rank_values[str(move.card.rank)] > rank_values[str(leader_move.cards[0].rank)] or str(move.card.suit) == str(perspective.get_trump_suit()):
                                return move
                        elif str(leader_move.cards[0].suit) == str(perspective.get_trump_suit()) and rank_values[str(move.card.rank)] > rank_values[str(leader_move.cards[0].rank)]:
                            return move

            return self.delegate_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
