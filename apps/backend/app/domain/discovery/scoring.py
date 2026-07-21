"""Deterministic scoring seam for future recommendation models."""


class RecommendationScorer:
    def score(self, profile, shared_interest_count: int) -> tuple[int, int, str]:
        """Higher tuples rank first; replace this implementation with ML later."""
        return (
            shared_interest_count,
            profile.profile_completion_percentage,
            profile.username,
        )
