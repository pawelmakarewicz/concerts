"""Мой вкус: оценки с Radio Paradise → список артистов с оценками."""

# Python: `csv` и `io` — стандартная библиотека, ставить ничего не надо (в Node нужен пакет).
import csv
import io

import httpx
from pydantic import BaseModel

RP_URL = "https://api.radioparadise.com/siteapi.php"


# Python: класс-наследник BaseModel — это и тип, и схема проверки (как `type` + `z.object` в TS).
class Artist(BaseModel):
    name: str
    rating: int  # 1–10, максимум по его песням


def download_csv(user_id: str) -> str:
    """Скачивает все мои оценки (1–10) в CSV. Логин не нужен, только id профиля."""
    # Python: httpx.get синхронный — ждёт ответа прямо здесь, без await.
    response = httpx.get(
        RP_URL,
        params={
            "file": "music::download-favorites",
            "lower_limit": 1,
            "upper_limit": 10,
            "user_id": user_id,
            "format": "csv",
        },
        timeout=30,
    )
    # Python: в отличие от axios, httpx не бросает ошибку на 404/500 сам — просим явно.
    response.raise_for_status()
    return response.text


def parse_artists(csv_text: str, min_rating: int) -> list[Artist]:
    """CSV `title,artist,album,year,rating` → артисты, оценка = максимум по песням."""
    # Python: DictReader отдаёт каждую строку как словарь {"title": ..., "artist": ...}.
    # lstrip("﻿") убирает невидимый BOM в начале файла, если он есть.
    reader = csv.DictReader(io.StringIO(csv_text.lstrip("﻿")))
    if not reader.fieldnames or not {"artist", "rating"} <= set(reader.fieldnames):
        raise ValueError(f"Неожиданный CSV от Radio Paradise: {reader.fieldnames}")

    best: dict[str, int] = {}
    for row in reader:
        name = row["artist"].strip()
        rating = int(row["rating"])  # Python: "8" + 0 не сработает, строку переводим в число явно
        # Python: dict.get(ключ, 0) — вернёт 0, если ключа нет (обычный d[ключ] бросил бы KeyError).
        best[name] = max(best.get(name, 0), rating)

    if not best:
        raise ValueError("Radio Paradise вернул пустой список оценок — проверь RP_USER_ID")

    # Python: это list comprehension — то же, что .filter(...).map(...) в JS, одной строкой.
    artists = [Artist(name=n, rating=r) for n, r in best.items() if r >= min_rating]
    # Сначала высокие оценки, внутри — по алфавиту. Минус перед числом = по убыванию.
    artists.sort(key=lambda a: (-a.rating, a.name.lower()))
    return artists


def load_artists(user_id: str, min_rating: int) -> list[Artist]:
    if not user_id:
        raise ValueError(
            "Не задан RP_USER_ID в .env (число из radioparadise.com/account/profile/<id>)"
        )
    return parse_artists(download_csv(user_id), min_rating)
