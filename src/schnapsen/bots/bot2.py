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
            game_history = perspective.get_game_history()
            if not len(game_history) == 1:
                game_history.pop()
                last_game = game_history.pop()
                is_leader_in_previous_trick = last_game[0].am_i_leader()
                played_marriage_in_previous_trick = False
                if not last_game[1].is_trump_exchange() and last_game[1].as_partial().leader_move.is_marriage():
                    played_marriage_in_previous_trick = True

                valid_moves = [move for move in perspective.valid_moves()]

                if is_leader_in_previous_trick and played_marriage_in_previous_trick:
                    for move in valid_moves:
                        if str(move.cards[0].rank) == "ACE" or (str(move.cards[0].suit) == str(perspective.get_trump_suit()) and str(move.cards[0].rank) in ["KING", "TEN", "ACE"]):
                            return move
                
                else:
                    can_play_marriage = False
                    can_play_strong_trump = False
                    has_ace = False
                    trump_marriage = False
                    chosen_move = None

                    for move in valid_moves:
                        if move.is_marriage():
                            can_play_marriage = True
                            chosen_move = move
                            if str(move.king_card.suit) == str(perspective.get_trump_suit()):
                                trump_marriage = True
                            break
                    
                    hand = perspective.get_hand().get_cards()
                    for card in hand:
                        if str(card.rank) == "ACE":
                            has_ace = True
                            break
                        if str(card.suit) == perspective.get_trump_suit() and str(card.rank) in ["KING", "TEN", "ACE"]:
                            can_play_strong_trump = True
                            break

                    if can_play_marriage and (can_play_strong_trump or has_ace or trump_marriage):
                        return chosen_move

            return self.delegate_phase1.get_move(perspective, leader_move)
        
        elif perspective.get_phase() == GamePhase.TWO:
            return self.delegate_phase2.get_move(perspective, leader_move)
