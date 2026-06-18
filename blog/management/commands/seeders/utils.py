import random
from datetime import timedelta


def random_time(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def power_law_weights(n, top_n, top_share):
    weights = [1.0] * n
    bonus = (top_share * n) / max(top_n, 1)
    for i in range(min(top_n, n)):
        weights[i] = 1.0 + bonus
    return weights


def long_tail_weights(n, top_pct, top_share):
    weights = [1.0] * n
    top_n = max(1, int(n * top_pct))
    bonus = (top_share * n) / top_n
    for i in range(top_n):
        weights[i] = 1.0 + bonus
    return weights
