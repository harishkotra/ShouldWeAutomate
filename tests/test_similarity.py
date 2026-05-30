import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.similarity import compute_similarity


SCORES_A = {
    "data_quality": 80,
    "process_stability": 75,
    "exception_rate": 70,
    "decision_complexity": 85,
    "integration_readiness": 90,
    "governance_risk": 80,
    "roi_potential": 85,
}

SCORES_B = {
    "data_quality": 78,
    "process_stability": 72,
    "exception_rate": 68,
    "decision_complexity": 82,
    "integration_readiness": 88,
    "governance_risk": 78,
    "roi_potential": 82,
}

SCORES_Z = {
    "data_quality": 5,
    "process_stability": 10,
    "exception_rate": 15,
    "decision_complexity": 8,
    "integration_readiness": 12,
    "governance_risk": 5,
    "roi_potential": 20,
}


def test_compute_similarity_identical():
    sim = compute_similarity(SCORES_A, SCORES_A)
    assert sim == 100.0


def test_compute_similarity_similar():
    sim = compute_similarity(SCORES_A, SCORES_B)
    assert 80 <= sim <= 100


def test_compute_similarity_different():
    sim = compute_similarity(SCORES_A, SCORES_Z)
    assert sim < 50


def test_compute_similarity_opposite():
    far = {k: 100 - v for k, v in SCORES_A.items()}
    sim = compute_similarity(SCORES_A, far)
    assert sim < 45


def test_compute_similarity_unknown_dims():
    sim = compute_similarity({"unknown": 50}, {"unknown": 50})
    assert sim == 100.0
