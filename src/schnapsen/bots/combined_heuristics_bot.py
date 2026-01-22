from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GamePhase
import random

from .rdeep import RdeepBot
from .alphabeta import AlphaBetaBot


class CombinedHeuristicsBot(Bot):
    """
    Unified bot combining heuristics from Bot1 to Bot5.

    Phase 1 (priority order):
    1. Trump exchange if valuable or completes marriage
    2. Play strong marriages
    3. When talon <= 2 and following, try to secure the lead
    4. Follower play with trump control logic:
        - No trump control: win cheaply or discard low
        - Trump control: preserve high cards, win minimally
    5. Fallback to Rdeep

    Phase 2:
        Alpha-beta pruning
    """

    def __init__(self, num_samples: int, depth: int, rand: random.Random,
                 name: Optional[str] = None) -> None:
        super().__init__(name)
        self.delegate_phase1 = RdeepBot(num_samples=num_samples, depth=depth, rand=rand)
        self.delegate_phase2 = AlphaBetaBot()
        self.rand = rand


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
            valid_moves = [move for move in perspective.valid_moves()]
            trump = perspective.get_trump_suit()

            if perspective.am_i_leader():
                exchange = None
                for move in valid_moves:
                    if move.is_trump_exchange():
                        exchange = move
                        break

                if exchange:
                    trump_card = perspective.get_trump_card()
                    has_king = any(str(card.rank) == "KING" and str(card.suit) == str(trump) for card in perspective.get_hand().get_cards())
                    has_queen = any(str(card.rank) == "QUEEN" and str(card.suit) == str(trump) for card in perspective.get_hand().get_cards())

                    if (str(trump_card.rank) in ["ACE", "TEN"] or (str(trump_card.rank) in ["KING", "QUEEN"] and (has_king or has_queen))):
                        return exchange

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

            if perspective.get_talon_size() <= 2 and not perspective.am_i_leader():
                regular_moves = [move.as_regular_move() for move in valid_moves if move.is_regular_move()]
                lead_card = leader_move.cards[0]

                for move in regular_moves:
                    if ((str(move.card.suit) == str(trump) and str(lead_card.suit) != str(trump))
                        or (str(move.card.suit) == str(lead_card.suit) and self.rank_value(str(move.card.rank)) > self.rank_value(str(lead_card.rank)))):
                        return move

            if not perspective.am_i_leader():
                regular_moves = [move.as_regular_move() for move in valid_moves if move.is_regular_move()]
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
                else:
                    if winning:
                        return winning
                    if lowest:
                        return lowest

            return self.delegate_phase1.get_move(perspective, leader_move)

        return self.delegate_phase2.get_move(perspective, leader_move)
