# concerts

Следит за афишами залов (начиная с NOSPR) и пишет в Telegram о концертах в моём вкусе. Подробности — в [PLAN.md](PLAN.md).

```sh
cp .env.example .env   # заполнить
uv run python -m concerts
uv run pytest
uv run ruff check .
```
