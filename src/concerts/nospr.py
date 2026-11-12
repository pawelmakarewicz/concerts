"""Афиша NOSPR (Катовице): страницы месяцев → события, страница события → подробности."""

import hashlib
from datetime import date, datetime
from zoneinfo import ZoneInfo  # Python: часовые пояса встроены, отдельная библиотека не нужна

import httpx
from pydantic import BaseModel
from selectolax.lexbor import LexborHTMLParser

BASE_URL = "https://nospr.org.pl"
VENUE = "NOSPR"
TZ = ZoneInfo("Europe/Warsaw")
# Афиша публикуется на сезон вперёд, и в ней бывают пустые месяцы (лето),
# поэтому идём на фиксированное число месяцев, а не до первого пустого.
MONTHS_AHEAD = 18


class Event(BaseModel):
    id: str  # стабильный: хеш ссылки на событие
    venue: str
    title: str
    starts_at: datetime
    url: str
    hall: str | None = None  # "Sala koncertowa", "Sala kameralna"…
    categories: list[str] = []  # "JazzKLUB", "Edukacja"… — подсказка для ИИ
    # Ниже — со страницы события (fetch_details), в списке месяца их нет.
    performers: list[str] = []
    program: list[str] = []  # "Композитор: произведение"
    description: str | None = None


def _text(node) -> str:
    """Текст узла с нормальными пробелами (в HTML их бывает сколько угодно)."""
    # Python: " ".join(s.split()) — стандартный приём «схлопнуть все пробелы и переносы в один».
    return " ".join(node.text(separator=" ").split()) if node else ""


def _event_id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def parse_month(html: str, now: datetime) -> list[Event]:
    """Страница месяца → события. Прошедшие (раздел «Wydarzenia archiwalne») пропускаем."""
    tree = LexborHTMLParser(html)
    events = []
    for row in tree.css("div.calendar__row"):
        day = date.fromisoformat(row.css_first("time").attributes["datetime"])
        for tile in row.css("div.tile--calendar"):
            hh, mm = _text(tile.css_first("span.hour")).split(":")
            starts_at = datetime(day.year, day.month, day.day, int(hh), int(mm), tzinfo=TZ)
            if starts_at < now:
                continue
            url = BASE_URL + tile.css_first("a.tile__link").attributes["href"]
            events.append(
                Event(
                    id=_event_id(url),
                    venue=VENUE,
                    title=_text(tile.css_first("h3.tile__title")),
                    starts_at=starts_at,
                    url=url,
                    hall=_text(tile.css_first("p.description")) or None,
                    categories=[_text(c) for c in tile.css("div.category")],
                )
            )
    return events


def parse_details(html: str, event: Event) -> Event:
    """Страница события → исполнители, программа, описание."""
    tree = LexborHTMLParser(html)
    performers, program = [], []
    for block in tree.css("div.program"):
        category = _text(block.css_first("div.program__category"))
        if category == "Program":
            composer = ""
            # Python: в блоке программы идут по очереди «композитор», «произведение», …
            for node in block.css("div.program__person, div.program__name"):
                if "program__person" in node.attributes.get("class", ""):
                    composer = _text(node)
                else:
                    program.append(f"{composer}: {_text(node)}" if composer else _text(node))
        else:  # "Dyrygent", "Wykonawcy", "Soliści"…
            # Имя — в <strong>, роль («– sopran») идёт после него.
            for person in block.css("div.program__person"):
                name = _text(person.css_first("strong")) or _text(person)
                performers.append(name.rstrip(":"))
    # Python: model_copy(update=...) — как { ...event, performers } в JS: новый объект.
    return event.model_copy(
        update={
            "performers": performers,
            "program": program,
            "description": _text(tree.css_first("div.text")) or None,
        }
    )


def _months(start: date, count: int) -> list[str]:
    """['2026-11', '2026-12', '2027-01', …]"""
    months = []
    year, month = start.year, start.month
    for _ in range(count):
        months.append(f"{year}-{month:02d}")  # :02d — дополнить нулём до двух цифр
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=BASE_URL,
        headers={"User-Agent": "concerts-bot/0.1"},
        timeout=30,
        follow_redirects=True,
    )


def fetch_events(now: datetime | None = None) -> list[Event]:
    """Вся опубликованная афиша (только список, без подробностей)."""
    now = now or datetime.now(TZ)
    events = []
    # Python: `with` закрывает соединение в конце блока, даже если внутри была ошибка
    # (похоже на try/finally или `using` в TS).
    with _client() as client:
        for month in _months(now.date(), MONTHS_AHEAD):
            response = client.get("/pl/kalendarz/", params={"miesiac": month})
            response.raise_for_status()
            events += parse_month(response.text, now)
    if not events:
        # Ноль событий на полтора года вперёд — это сломанный парсер, а не «ничего нового».
        raise RuntimeError("NOSPR: не найдено ни одного события — сайт поменялся?")
    return events


def fetch_details(event: Event) -> Event:
    with _client() as client:
        response = client.get(event.url)
        response.raise_for_status()
    return parse_details(response.text, event)
