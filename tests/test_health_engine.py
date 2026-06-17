"""Tests for the Infrastructure Health Scoring Engine."""

import pytest
from datetime import date, timedelta
from app.services.health_engine import (
    compute_age_score,
    compute_inspection_delay_score,
    compute_damage_score,
    compute_maintenance_frequency_score,
    calculate_health_score,
    get_recommended_action,
    HEALTHY_MAX,
    WARNING_MAX,
)


class TestAgeScore:
    def test_new_asset_has_low_age_score(self):
        score = compute_age_score(date.today().year - 1, "road")
        assert score < 15

    def test_very_old_asset_has_high_age_score(self):
        score = compute_age_score(1960, "road")
        assert score > 70

    def test_age_score_within_bounds(self):
        for year in [1950, 1980, 2000, 2020]:
            score = compute_age_score(year, "bridge")
            assert 0 <= score <= 100

    def test_bridge_has_longer_design_life_than_road(self):
        old_year = 1980
        bridge_score = compute_age_score(old_year, "bridge")
        road_score = compute_age_score(old_year, "road")
        assert road_score >= bridge_score  # road degrades faster


class TestInspectionDelayScore:
    def test_recent_inspection_has_low_score(self):
        recent = date.today() - timedelta(days=30)
        score = compute_inspection_delay_score(recent, "road")
        assert score < 10

    def test_never_inspected_has_high_score(self):
        score = compute_inspection_delay_score(None, "road")
        assert score >= 85

    def test_overdue_inspection_has_high_score(self):
        overdue = date.today() - timedelta(days=700)
        score = compute_inspection_delay_score(overdue, "road")
        assert score > 50

    def test_score_within_bounds(self):
        score = compute_inspection_delay_score(date(2010, 1, 1), "bridge")
        assert 0 <= score <= 100


class TestDamageScore:
    def test_no_damage_no_reports_is_zero(self):
        assert compute_damage_score([], 0) == 0.0

    def test_high_damage_levels_give_high_score(self):
        score = compute_damage_score([9.0, 8.5, 9.5], 5)
        assert score > 80

    def test_many_reports_increase_score(self):
        score_low = compute_damage_score([], 1)
        score_high = compute_damage_score([], 10)
        assert score_high > score_low

    def test_score_capped_at_100(self):
        score = compute_damage_score([10.0] * 20, 50)
        assert score <= 100


class TestHealthScoreIntegration:
    def test_new_well_maintained_asset_is_healthy(self):
        result = calculate_health_score(
            installation_year=date.today().year - 2,
            asset_type="road",
            last_inspection_date=date.today() - timedelta(days=60),
            damage_levels=[0.5, 1.0],
            citizen_report_count=0,
            maintenance_dates=[date.today() - timedelta(days=90)]
        )
        assert result["risk_level"] == "healthy"
        assert result["health_score"] <= HEALTHY_MAX

    def test_old_uninspected_damaged_asset_is_critical(self):
        result = calculate_health_score(
            installation_year=1965,
            asset_type="road",
            last_inspection_date=date(2015, 1, 1),
            damage_levels=[9.5, 8.5, 9.0],
            citizen_report_count=8,
            maintenance_dates=[date(2015, 6, 1)]
        )
        assert result["risk_level"] == "critical"
        assert result["health_score"] > WARNING_MAX

    def test_health_score_returns_breakdown(self):
        result = calculate_health_score(
            installation_year=2005,
            asset_type="bridge",
            last_inspection_date=date.today() - timedelta(days=200),
            damage_levels=[3.0],
            citizen_report_count=1,
            maintenance_dates=[date.today() - timedelta(days=300)]
        )
        assert "breakdown" in result
        assert all(k in result["breakdown"] for k in [
            "age_score", "inspection_delay_score", "damage_score", "maintenance_score"
        ])

    def test_score_always_between_0_and_100(self):
        for year in [1950, 1985, 2010, 2023]:
            result = calculate_health_score(
                installation_year=year,
                asset_type="bridge",
                last_inspection_date=None,
                damage_levels=[5.0],
                citizen_report_count=2,
                maintenance_dates=[]
            )
            assert 0 <= result["health_score"] <= 100

    def test_recommended_action_for_critical(self):
        action = get_recommended_action(85, "critical")
        assert "IMMEDIATE" in action or "URGENT" in action

    def test_recommended_action_for_healthy(self):
        action = get_recommended_action(15, "healthy")
        assert "ROUTINE" in action
