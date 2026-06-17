"""
Risk Propagation Engine
========================
Models how infrastructure failures cascade through connected assets.

Key insight: Infrastructure assets are interdependent.
When a critical asset fails, connected downstream assets face elevated risk.

Algorithm: BFS graph traversal with risk decay per hop.
Risk decays by 30% per connection hop to model diminishing impact.

Example propagation chains:
  pipeline (critical) → road (elevated warning)
  bridge (critical)   → road (elevated warning)
  drainage (critical) → road (flood risk)
"""

from typing import Dict, List, Set, Tuple
from collections import deque
import logging

logger = logging.getLogger(__name__)

# Risk propagation rules: source_type → [affected_types]
PROPAGATION_RULES = {
    "pipeline": ["road", "public_facility"],
    "bridge": ["road"],
    "drainage": ["road", "pipeline"],
    "road": ["public_facility"],
    "street_light": ["road"],
    "public_facility": [],
}

# Risk score contribution when propagated (% of source health score)
PROPAGATION_DECAY = 0.70   # Each hop reduces risk by 30%
MAX_PROPAGATION_HOPS = 3   # Limit traversal depth
PROPAGATION_THRESHOLD = 61  # Only propagate if asset is critical


def build_adjacency_graph(connections: List[dict]) -> Dict[int, List[int]]:
    """
    Build an adjacency graph from asset connection records.
    connections: list of dicts with keys: asset_id, connected_asset_id
    """
    graph: Dict[int, List[int]] = {}
    for conn in connections:
        src = conn["asset_id"]
        dst = conn["connected_asset_id"]
        if src not in graph:
            graph[src] = []
        graph[src].append(dst)
    return graph


def propagate_risk(
    source_asset_id: int,
    source_health_score: float,
    graph: Dict[int, List[int]],
    all_assets: Dict[int, dict]
) -> Dict[int, dict]:
    """
    BFS traversal from a critical asset to propagate elevated risk to neighbors.

    Returns:
        dict mapping asset_id → {propagated_risk_delta, hops, source_id}
    """
    if source_health_score < PROPAGATION_THRESHOLD:
        return {}

    propagated = {}
    visited: Set[int] = {source_asset_id}
    queue = deque()

    # Start: direct neighbors
    for neighbor_id in graph.get(source_asset_id, []):
        queue.append((neighbor_id, 1, source_health_score))

    while queue:
        asset_id, hops, incoming_risk = queue.popleft()

        if asset_id in visited or hops > MAX_PROPAGATION_HOPS:
            continue
        visited.add(asset_id)

        risk_delta = incoming_risk * (PROPAGATION_DECAY ** hops) * 0.3
        risk_delta = round(min(risk_delta, 40.0), 2)  # Cap propagated risk at 40 pts

        if asset_id in propagated:
            # Take max risk contribution
            propagated[asset_id]["risk_delta"] = max(
                propagated[asset_id]["risk_delta"], risk_delta
            )
        else:
            propagated[asset_id] = {
                "risk_delta": risk_delta,
                "hops": hops,
                "source_id": source_asset_id,
                "source_score": source_health_score,
            }

        # Continue BFS to next hops
        for neighbor_id in graph.get(asset_id, []):
            if neighbor_id not in visited:
                queue.append((neighbor_id, hops + 1, risk_delta))

    return propagated


def compute_network_risk(
    assets: List[dict],
    connections: List[dict]
) -> Dict[int, dict]:
    """
    Full network risk analysis across all assets.

    Args:
        assets: list of dicts with id, health_score, risk_level, asset_type, asset_name
        connections: list of dicts with asset_id, connected_asset_id

    Returns:
        dict: asset_id → {
            original_score, propagated_delta, adjusted_score,
            risk_level, propagated_from
        }
    """
    graph = build_adjacency_graph(connections)
    asset_map = {a["id"]: a for a in assets}

    # Initialize results
    results: Dict[int, dict] = {}
    for asset in assets:
        results[asset["id"]] = {
            "asset_id": asset["id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "original_score": asset["health_score"],
            "propagated_delta": 0.0,
            "adjusted_score": asset["health_score"],
            "risk_level": asset["risk_level"],
            "propagated_from": []
        }

    # Run propagation from each critical asset
    for asset in assets:
        if asset["health_score"] >= PROPAGATION_THRESHOLD:
            propagated = propagate_risk(
                asset["id"],
                asset["health_score"],
                graph,
                asset_map
            )

            for target_id, prop_data in propagated.items():
                if target_id in results:
                    results[target_id]["propagated_delta"] = round(
                        results[target_id]["propagated_delta"] + prop_data["risk_delta"], 2
                    )
                    results[target_id]["propagated_from"].append({
                        "source_id": asset["id"],
                        "source_name": asset["asset_name"],
                        "risk_delta": prop_data["risk_delta"],
                        "hops": prop_data["hops"]
                    })

    # Recalculate adjusted scores and risk levels
    for asset_id, result in results.items():
        adjusted = min(100, result["original_score"] + result["propagated_delta"])
        result["adjusted_score"] = round(adjusted, 2)

        if adjusted <= 30:
            result["adjusted_risk_level"] = "healthy"
        elif adjusted <= 60:
            result["adjusted_risk_level"] = "warning"
        else:
            result["adjusted_risk_level"] = "critical"

    return results


def get_cascade_summary(network_risk: Dict[int, dict]) -> dict:
    """Summarize cascade impact across the network."""
    total = len(network_risk)
    affected = sum(
        1 for r in network_risk.values()
        if r["propagated_delta"] > 0
    )
    escalated = sum(
        1 for r in network_risk.values()
        if r.get("adjusted_risk_level", "") != r["risk_level"]
        and r["propagated_delta"] > 0
    )

    return {
        "total_assets": total,
        "directly_critical": sum(1 for r in network_risk.values() if r["risk_level"] == "critical"),
        "propagation_affected": affected,
        "risk_escalated": escalated,
        "network_health_index": round(
            100 - (sum(r["adjusted_score"] for r in network_risk.values()) / total), 2
        ) if total else 0
    }
