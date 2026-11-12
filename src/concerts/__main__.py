from concerts.config import Settings


def main() -> None:
    settings = Settings()
    print(f"concerts: модель {settings.ai_model}, порог {settings.notify_min_score}")


if __name__ == "__main__":
    main()
