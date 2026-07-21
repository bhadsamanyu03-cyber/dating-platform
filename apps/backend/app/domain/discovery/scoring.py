"""Deterministic scoring configuration for future recommendation models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationWeights:
    shared_interests: int = 100
    profile_completeness: int = 1
    verified: int = 25
    recent_activity: int = 10
    freshness: int = 5


class RecommendationScorer:
    def __init__(self, weights: RecommendationWeights | None = None):
        self.weights = weights or RecommendationWeights()

    def score(self, profile, shared_interest_count: int) -> tuple[int, int, str]:
        """Stable in-memory seam; SQL ranking uses the same component weights."""
        verified = int(getattr(profile, "is_email_verified", False))
        recent = int(getattr(profile, "is_active_recently", False))
        freshness = int(getattr(profile, "is_fresh", False))
        total = (
            shared_interest_count * self.weights.shared_interests
            + profile.profile_completion_percentage * self.weights.profile_completeness
            + verified * self.weights.verified
            + recent * self.weights.recent_activity
            + freshness * self.weights.freshness
        )
        return (
            total,
            shared_interest_count,
            profile.username,
        )
