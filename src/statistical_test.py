from statistics import mean
from scipy.stats import ttest_ind, binomtest
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np


def plot_score_distribution(test_scores: list[list[int]]):
    """
    plot_score_distribution serves to represent the game point distribution (columns for the number of times each bot, including the baseline bot, has scored 0, 1, 2 or 3 game points)
    
    :param test_scores: List of lists containing the number of points each bot has scored in each game
    """
    scores = [0, 1, 2, 3]
    num_lists = len(test_scores)

    counts = []
    for lst in test_scores:
        counts.append([lst.count(score) for score in scores])

    counts = np.array(counts)

    x = np.arange(len(scores))
    bar_width = 0.15

    plt.figure(figsize=(9, 5))

    for i in range(num_lists):
        plt.bar(
            x + i * bar_width,
            counts[i],
            width=bar_width,
            label=f"Bot {i}"
        )

    plt.xlabel("Game Points Scored")
    plt.ylabel("Frequency")
    plt.title("Histogram of scored game points")
    plt.xticks(x + bar_width * 2, scores)
    plt.gca().yaxis.set_major_locator(MultipleLocator(100))
    plt.gca().yaxis.set_minor_locator(MultipleLocator(20))
    plt.grid(which='major', axis='y', linestyle='--', linewidth=0.8, alpha=0.7)
    plt.grid(which='minor', axis='y', linestyle=':', linewidth=0.5, alpha=0.5)
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_winrates(bot_names: list[str], winrates: list[float]):
    """
    plot_winrates serves to present the win rates of each bot as columns in a graph and the win rate of the baseline is represented as a line (threshold) to be reached/surpassed
    
    :param bot_names: List of names for the bots corresponding to the appropriate win rates
    :param winrates: List of win rates for each bot (including the baseline bot) corresponding to the appropriate names
    """
    plt.figure(figsize=(8,5))
    plt.bar(bot_names[1:], winrates[1:])
    plt.axhline(winrates[0], color="red", linestyle="--", label="Baseline win rate")
    plt.ylabel("Win Rate")
    plt.title("Win Rate vs Baseline")
    plt.legend()
    plt.show()


def game_points_test(test_bot_points: list[int], baseline_bot_points: list[int]):
    """
    game_points_test is a function where the mean difference of two samples and the p_value from an independent T-test are calculated and returned as a dictionary
    
    :param test_bot_points: points scored by the bot being tested
    :param baseline_bot_points: points scored by the baseline bot
    """
    if len(test_bot_points) < 30:
        raise ValueError("Need at least 30 games for statistical significance")

    diffs = [a - b for a, b in zip(test_bot_points, baseline_bot_points)]
    mean_diff = mean(diffs)

    t_stat, p_value = ttest_ind(test_bot_points, baseline_bot_points)

    return {
        "mean_diff": mean_diff,
        "p_value": p_value,
    }


def winrate_test(wins: float, total_games: float):
    """
    winrate_test is a function where the win_rate and the p_value from a binomial test are calculated and returned as a dictionary
    
    :param wins: number of games won by the tested bot
    :param total_games: number of games being played by the tested bot
    """
    result = binomtest(wins, total_games, p=0.5, alternative="greater")
    return {
        "win_rate": wins / total_games,
        "p_value": result.pvalue
    }


bot_names = []
winrates = []
test_scores = []
baseline_scores = []

for i in range(6):
    test_wins = 0
    test_score = []

    with open(f"experiment_data/Bot{i}_data.txt", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            test_score.append(int(row[0]))

            if int(row[0]) > int(row[1]):
                test_wins += 1

        test_scores.append(test_score)

    total_games = len(test_score)

    game_points_stats = game_points_test(test_score, test_scores[0])
    win_stats = winrate_test(test_wins, total_games)

    winrates.append(win_stats["win_rate"])
    bot_names.append(f"Bot{i}")

    print("=" * 47)
    print(f"Bot{i} RESULTS")
    print(f"Games played: {total_games}")
    print(f"Win rate: {win_stats['win_rate']:.2%} (p = {win_stats['p_value']:.4f})")
    print(f"Mean score difference: {game_points_stats['mean_diff']:.2f}")
    print(f"Independent t-test p-value: {game_points_stats['p_value']:.4f}")

    if game_points_stats["p_value"] < 0.05:
        print("→ Score difference is statistically significant")
    else:
        print("→ No statistically significant score difference")


plot_score_distribution(test_scores)
plot_winrates(bot_names, winrates)
