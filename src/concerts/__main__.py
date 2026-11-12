from concerts.config import Settings
from concerts.nospr import fetch_events
from concerts.taste import load_artists


def main() -> None:
    settings = Settings()
    artists = load_artists(settings.rp_user_id, settings.min_rating)
    print(f"Мои артисты с оценкой ≥ {settings.min_rating}: {len(artists)}")

    events = fetch_events()
    print(f"\nАфиша NOSPR: {len(events)} событий")
    for e in events:
        # Python: strftime — форматирование даты, %d.%m.%Y %H:%M → 14.12.2026 19:00
        print(f"  {e.starts_at:%d.%m.%Y %H:%M}  {e.title}  [{', '.join(e.categories)}]")


if __name__ == "__main__":
    main()
