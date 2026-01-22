from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GamePhase, GameState, GamePlayEngine
import random

from .rdeep import RdeepBot
from .alphabeta import AlphaBetaBot

class Bot3(Bot):
    """
    Heuristic bot tackling phase 1 (resort to rdeep in phase 1 if unable to come up with move) and alpha-beta pruning in phase 2
    If you have trump control and are following a trick preserve your high cards (play lowest winning cards other than ten or ace. If that trick can't be won play lowest non-trump card)
    
    (this heuristic helps manage your high cards as to maximise your winnings and minimise the ones of your opponent.
    The idea is to ensure that high cards and trumps are not wasted on capturing the lead, but rather used once it is obtained for stronger play.)
    """
    def __init__(self, num_samples: int, depth: int, rand: random.Random, name: Optional[str] = None) -> None:
        """
        Create a new Bot3 bot.

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


    @staticmethod
    def rank_value(rank: str) -> int:
        return {"JACK": 2, "QUEEN": 3, "KING": 4, "TEN": 10, "ACE": 11}[rank]


    def has_trump_control(self, perspective: PlayerPerspective) -> bool:
        trump = perspective.get_trump_suit()
        score = 0
        for card in perspective.get_hand().get_cards():
            if str(card.suit) == str(trump):
                if str(card.rank) == "ACE":
                    score += 2
                else:
                    score += 1
        return score >= 3 or (perspective.get_talon_size() <= 2 and score >= 2)


    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            if not perspective.am_i_leader():
                regular_moves = [move.as_regular_move() for move in perspective.valid_moves() if move.is_regular_move()]
                trump = perspective.get_trump_suit()
                trump_control = self.has_trump_control(perspective)

                lowest = None
                lowest_val = 100
                winning = None
                winning_val = 100

                lead_card = leader_move.cards[0]

                for move in regular_moves:
                    val = self.rank_value(str(move.card.rank))
                    if str(move.card.suit) != str(trump):
                        if val < lowest_val:
                            lowest_val = val
                            lowest = move
                        if (str(move.card.suit) == str(lead_card.suit) and
                            val > self.rank_value(str(lead_card.rank)) and
                            val < winning_val):
                            winning_val = val
                            winning = move

                if trump_control:
                    if winning:
                        return winning
                    if lowest:
                        return lowest

            return self.delegate_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
