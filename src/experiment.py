from schnapsen.game import SchnapsenGamePlayEngine, Bot, PlayerPerspective, Move, RegularMove, GamePhase
from schnapsen.bots import RdeepAlphaBeta, Bot1, Bot2, Bot3, Bot4, Bot5
import random
import csv


def experiment_part_1(player1, player2) -> list[list[int], list[int]]:
    player1_points = []
    player2_points = []
    for _ in range(500):
        winner, game_points, score = engine.play_game(player1, player2, random.Random())
        if str(winner) != "rdeep_ab":
            player1_points.append(game_points)
            player2_points.append(0)
        else:
            player1_points.append(0)
            player2_points.append(game_points)
    return [player1_points, player2_points]


def experiment_part_2(player1, player2) -> list[list[int], list[int]]:
    player1_points = []
    player2_points = []
    for _ in range(500):
        winner, game_points, score = engine.play_game(player1, player2, random.Random())
        if str(winner) == "rdeep_ab":
            player1_points.append(game_points)
            player2_points.append(0)
        else:
            player1_points.append(0)
            player2_points.append(game_points)
    return [player1_points, player2_points]


def experiment(player1, player2, bot_number) -> list[list[int], list[int]]:
    player1_points1, player2_points1 = experiment_part_1(player1, player2)
    player2_points2, player1_points2 = experiment_part_2(player2, player1)
    player1_points, player2_points = player1_points1 + player1_points2, player2_points1 + player2_points2
    with open(f"experiment_data/Bot{bot_number}_data.txt", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([f"heuristic_bot_points", f"rdeep_alpa_beta_points"])
        for p1, p2 in zip(player1_points, player2_points):
            writer.writerow([p1, p2])

    return [player1_points, player2_points]


engine = SchnapsenGamePlayEngine()

rdeep_alpha_beta_bot = RdeepAlphaBeta(depth = 4, num_samples = 300, rand=random.Random(), name="rdeep_ab")
bot1 = Bot1(depth = 4, num_samples = 300, rand=random.Random(), name="bot1")
bot2 = Bot2(depth = 4, num_samples = 300, rand=random.Random(), name="bot2")
bot3 = Bot3(depth = 4, num_samples = 300, rand=random.Random(), name="bot3")
bot4 = Bot4(depth = 4, num_samples = 300, rand=random.Random(), name="bot4")
bot5 = Bot5(depth = 4, num_samples = 300, rand=random.Random(), name="bot5")

bot1_points, rdeep_alpha_beta_points = experiment(bot1, rdeep_alpha_beta_bot, 1)
bot2_points, rdeep_alpha_beta_points = experiment(bot2, rdeep_alpha_beta_bot, 2)
bot3_points, rdeep_alpha_beta_points = experiment(bot3, rdeep_alpha_beta_bot, 3)
bot4_points, rdeep_alpha_beta_points = experiment(bot4, rdeep_alpha_beta_bot, 4)
bot5_points, rdeep_alpha_beta_points = experiment(bot5, rdeep_alpha_beta_bot, 5)
