"""Smoke tests for elfrfdet.models.make_rf — pin defaults to detect drift."""

from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier

from elfrfdet.models import make_rf


def test_make_rf_returns_random_forest_with_pinned_defaults() -> None:
    rf = make_rf()
    assert isinstance(rf, RandomForestClassifier)
    assert rf.n_estimators == 100
    assert rf.random_state == 42
    assert rf.n_jobs == -1
    assert rf.max_depth is None


def test_make_rf_forwards_overrides() -> None:
    rf = make_rf(n_estimators=10, max_depth=5, random_state=7, n_jobs=2)
    assert rf.n_estimators == 10
    assert rf.max_depth == 5
    assert rf.random_state == 7
    assert rf.n_jobs == 2
