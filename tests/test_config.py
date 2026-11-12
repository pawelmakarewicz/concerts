from concerts.config import Settings


def test_defaults(monkeypatch):
    monkeypatch.delenv("NOTIFY_MIN_SCORE", raising=False)
    assert Settings(_env_file=None).notify_min_score == 7


def test_env_override(monkeypatch):
    monkeypatch.setenv("NOTIFY_MIN_SCORE", "9")
    assert Settings(_env_file=None).notify_min_score == 9
