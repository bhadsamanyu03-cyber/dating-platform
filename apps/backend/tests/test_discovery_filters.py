import pytest
from pydantic import ValidationError

from app.domain.discovery.schemas import DiscoveryFilters
from app.domain.discovery.scoring import RecommendationScorer, RecommendationWeights


def test_discovery_filters_reject_inverted_age_range() -> None:
    with pytest.raises(ValidationError, match="Minimum age"):
        DiscoveryFilters(min_age=40, max_age=20)


def test_discovery_filters_accept_supported_values() -> None:
    filters = DiscoveryFilters(
        min_age=21, max_age=40, gender="Woman", verified_only=True, active_recently=True
    )
    assert filters.verified_only and filters.active_recently and filters.gender == "Woman"


def test_recommendation_scorer_is_deterministic() -> None:
    profile = type(
        "Profile",
        (),
        {
            "profile_completion_percentage": 100,
            "username": "alex",
            "is_email_verified": True,
            "is_active_recently": True,
            "is_fresh": False,
        },
    )()
    scorer = RecommendationScorer(RecommendationWeights(shared_interests=10, verified=5))
    assert scorer.score(profile, 2) == (135, 2, "alex")
