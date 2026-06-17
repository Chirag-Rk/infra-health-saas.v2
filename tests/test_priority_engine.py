"""Tests for the Maintenance Priority Engine."""

import pytest
from app.services.priority_engine import (
    calculate_priority_score,
    rank_assets_by_priority,
    compute_safety_risk_score,
    compute_population_impact,
    compute_infrastructure_importance,
    compute_cost_urgency,
)


class TestSafetyRiskScore:
    def test_critical_asset_amplified(self):
        score = compute_safety_risk_score(65, "critical", 0)
        assert score > 65

    def test_cascade_adds_to_score(self):
        base = compute_safety_risk_score(50, "warning", 0)
        cascaded = compute_safety_risk_score(50, "warning", 30)
        assert cascaded > base

    def test_capped_at_100(self):
        score = compute_safety_risk_score(100, "critical", 50)
        assert score <= 100


class TestPopulationImpact:
    def test_pipeline_has_high_impact(self):
        score = compute_population_impact("pipeline", 0)
        assert score >= 90

    def test_street_light_has_low_impact(self):
        score = compute_population_impact("street_light", 0)
        assert score < 50

    def test_more_reports_increase_impact(self):
        low = compute_population_impact("road", 1)
        high = compute_population_impact("road", 10)
        assert high > low


class TestInfrastructureImportance:
    def test_bridge_is_highly_important(self):
        score = compute_infrastructure_importance("bridge", 0)
        assert score >= 90

    def test_connections_increase_importance(self):
        base = compute_infrastructure_importance("road", 0)
        connected = compute_infrastructure_importance("road", 5)
        assert connected > base

    def test_capped_at_100(self):
        score = compute_infrastructure_importance("pipeline", 100)
        assert score <= 100


class TestCostUrgency:
    def test_older_asset_has_higher_urgency(self):
        young = compute_cost_urgency("bridge", 5)
        old = compute_cost_urgency("bridge", 50)
        assert old > young

    def test_score_within_bounds(self):
        for age in [0, 10, 30, 60]:
            score = compute_cost_urgency("road", age)
            assert 0 <= score <= 100


class TestPriorityScoreIntegration:
    def test_critical_asset_has_high_priority(self):
        result = calculate_priority_score(
            health_score=80,
            risk_level="critical",
            asset_type="bridge",
            age_years=40,
            citizen_reports=5,
            connections_count=4,
            propagated_delta=10,
        )
        assert result["priority_score"] > 70
        assert "EMERGENCY" in result["action"] or "URGENT" in result["action"]

    def test_healthy_asset_has_low_priority(self):
        result = calculate_priority_score(
            health_score=15,
            risk_level="healthy",
            asset_type="street_light",
            age_years=3,
            citizen_reports=0,
            connections_count=0,
            propagated_delta=0,
        )
        assert result["priority_score"] < 60

    def test_result_has_breakdown(self):
        result = calculate_priority_score(
            health_score=50,
            risk_level="warning",
            asset_type="road",
            age_years=15,
            citizen_reports=2,
            connections_count=2,
        )
        assert "breakdown" in result
        for k in ["safety_risk", "population_impact", "infrastructure_importance", "cost_urgency"]:
            assert k in result["breakdown"]


class TestRankAssetsFunction:
    def test_returns_correct_count(self):
        assets = [
            {"asset_id": i, "asset_name": f"Asset {i}", "asset_type": "road",
             "department": "Works", "health_score": i * 10,
             "risk_level": "critical" if i > 5 else "healthy",
             "installation_year": 2000, "citizen_report_count": 0,
             "connections_count": 0, "propagated_delta": 0}
            for i in range(1, 8)
        ]
        ranked = rank_assets_by_priority(assets)
        assert len(ranked) == len(assets)

    def test_ranked_in_descending_order(self):
        assets = [
            {"asset_id": 1, "asset_name": "Old Critical Bridge", "asset_type": "bridge",
             "department": "Works", "health_score": 85, "risk_level": "critical",
             "installation_year": 1965, "citizen_report_count": 6,
             "connections_count": 3, "propagated_delta": 20},
            {"asset_id": 2, "asset_name": "New Healthy Light", "asset_type": "street_light",
             "department": "Electric", "health_score": 10, "risk_level": "healthy",
             "installation_year": 2022, "citizen_report_count": 0,
             "connections_count": 0, "propagated_delta": 0},
        ]
        ranked = rank_assets_by_priority(assets)
        assert ranked[0]["asset_id"] == 1  # Bridge should rank higher
        assert ranked[0]["rank"] == 1

    def test_each_item_has_rank_field(self):
        assets = [
            {"asset_id": i, "asset_name": f"A{i}", "asset_type": "road",
             "department": "D", "health_score": 50, "risk_level": "warning",
             "installation_year": 2000, "citizen_report_count": 1,
             "connections_count": 1, "propagated_delta": 0}
            for i in range(3)
        ]
        ranked = rank_assets_by_priority(assets)
        ranks = [r["rank"] for r in ranked]
        assert sorted(ranks) == list(range(1, len(assets) + 1))
