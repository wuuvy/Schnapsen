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

    Trump control is:
        score = 0
        +2 if has trump Ace
        +1 per additional trump
        trump_control = score >= 3 or (perspective.get_talon_size() <= 2 and trump_score >= 2)
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


    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            if not perspective.am_i_leader():
                valid_moves = [move.as_regular_move() for move in perspective.valid_moves() if move.is_regular_move()]
                
                trump_score = 0
                trump_control = False
                minimal_card_value_move = None
                minimal_card_value = 100
                minimal_winning_card_value_move = None
                minimal_winning_card_value = 100
                rank_values = {"JACK" : 2, "QUEEN" : 3, "KING" : 4, "TEN" : 10, "ACE" : 11}

                for move in valid_moves:
                    if str(move.card.suit) == str(perspective.get_trump_suit()):
                        if str(move.card.rank) == "ACE":
                            trump_score += 2
                        else:
                            trump_score += 1
                    else:
                        if rank_values[str(move.card.rank)] < minimal_card_value:
                            minimal_card_value = rank_values[str(move.card.rank)]
                            minimal_card_value_move = move
                        if rank_values[str(move.card.rank)] < minimal_winning_card_value and rank_values[str(move.card.rank)] > rank_values[str(leader_move.cards[0].rank)]:
                            minimal_winning_card_value = rank_values[str(move.card.rank)]
                            minimal_winning_card_value_move = move

                if trump_score >= 3 or (perspective.get_talon_size() <= 2 and trump_score >= 2):
                    trump_control = True

                if trump_control:
                    if minimal_winning_card_value_move != None:
                        return minimal_winning_card_value_move
                    else:
                        return minimal_card_value_move

            return self.delegate_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
