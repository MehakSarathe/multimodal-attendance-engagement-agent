from src.fusion import calculate_engagement
from src.analytics import generate_recommendations

def test_no_media_returns_safe_placeholder():
    result = calculate_engagement({}, {})
    assert 0 <= result["score"] <= 100
    assert "not a validated" in result["interpretation"]

def test_recommendations_are_returned():
    result = calculate_engagement({}, {})
    recs = generate_recommendations(result, {}, {})
    assert len(recs) >= 2
