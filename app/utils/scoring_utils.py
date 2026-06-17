from typing import List


def normalize(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def weighted_average(values: List[float], weights: List[float]) -> float:
    if not values or len(values) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def percentile_rank(value: float, values: List[float]) -> float:
    if not values:
        return 0.0
    below = sum(1 for v in values if v < value)
    return round((below / len(values)) * 100, 1)


def score_to_label(score: float) -> str:
    if score <= 30:
        return "Healthy"
    elif score <= 60:
        return "Warning"
    else:
        return "Critical"


def format_score_display(score: float) -> str:
    label = score_to_label(score)
    return f"{score:.1f} ({label})"
