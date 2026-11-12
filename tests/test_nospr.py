from datetime import datetime

from concerts.nospr import TZ, Event, _months, parse_details, parse_month

# Урезанная копия настоящей разметки страницы месяца.
MONTH_HTML = """
<div class="grid-22 calendar__row" id="day-30"><div class="term">Poniedziałek
<time datetime="2026-11-30">30.11</time></div><div class="tiles tiles--calendar">
<div class="tile tile--calendar"><a href="/pl/kalendarz/cory-henry-and-trio-band" class="tile__link">
<span class="sr-only">Cory Henry</span></a>
<div class="tile__text tile__text--calendar"><div class="category">Zewnętrzny organizator koncertu</div>
<span>/</span><div class="category">Nowe w kalendarium</div></div>
<div class="tile__term tile__term--calendar"><span class="hour"><i class="icon-clock"></i>19:30</span></div>
<div class="tile__text tile__text--calendar">
<h3 class="tile__title tile__title--calendar">Cory Henry / „A Jam Good Time”</h3>
<p class="description">Sala koncertowa</p></div></div>
</div></div>
<h3 class="no-hits"><span>Wydarzenia archiwalne</span></h3>
<div class="grid-22 calendar__row" id="day-3"><div class="term">Wtorek
<time datetime="2026-11-03">03.11</time></div><div class="tiles tiles--calendar">
<div class="tile tile--calendar"><a href="/pl/kalendarz/jazzklub-wilkins" class="tile__link"></a>
<div class="tile__term tile__term--calendar"><span class="hour"><i class="icon-clock"></i>19:30</span></div>
<h3 class="tile__title tile__title--calendar">JazzKLUB / Immanuel Wilkins Quartet</h3></div>
</div></div>
"""

DETAILS_HTML = """
<div class="program"><div class="program__category">Dyrygent</div>
<div class="program__person"><strong><a href="/x">Christian  Arming</a></strong></div></div>
<div class="program"><div class="program__category">Wykonawcy</div>
<div class="program__person"><strong>NOSPR</strong></div>
<div class="program__person"><strong>Magdalena Lucjan</strong>– sopran</div></div>
<div class="program"><div class="program__category">Program</div>
<div class="program__person"><strong>Jacob Druckman</strong></div><div class="program__name">Prism </div>
<div class="program__spacer"></div>
<div class="program__person"><strong>Wolfgang Amadeus Mozart</strong></div>
<div class="program__name">Requiem d-moll KV 626</div></div>
<div class="text"><p>Msza żałobna <em>Requiem</em>.</p>
<p>Druga linia.</p></div>
"""

NOW = datetime(2026, 11, 12, 12, 0, tzinfo=TZ)


def test_parse_month_reads_tile():
    # Python: распаковка [event] = ... заодно проверяет, что событие ровно одно.
    [event] = parse_month(MONTH_HTML, NOW)
    assert event.title == "Cory Henry / „A Jam Good Time”"
    assert event.starts_at == datetime(2026, 11, 30, 19, 30, tzinfo=TZ)
    assert event.url == "https://nospr.org.pl/pl/kalendarz/cory-henry-and-trio-band"
    assert event.hall == "Sala koncertowa"
    assert event.categories == ["Zewnętrzny organizator koncertu", "Nowe w kalendarium"]


def test_parse_month_skips_past_events():
    assert all(e.starts_at >= NOW for e in parse_month(MONTH_HTML, NOW))


def test_id_is_stable():
    assert parse_month(MONTH_HTML, NOW)[0].id == parse_month(MONTH_HTML, NOW)[0].id


def test_parse_details():
    base = Event(id="x", venue="NOSPR", title="t", starts_at=NOW, url="u")
    event = parse_details(DETAILS_HTML, base)
    assert event.performers == ["Christian Arming", "NOSPR", "Magdalena Lucjan"]
    assert event.program == [
        "Jacob Druckman: Prism",
        "Wolfgang Amadeus Mozart: Requiem d-moll KV 626",
    ]
    assert event.description == "Msza żałobna Requiem . Druga linia."
    assert base.performers == []  # исходный объект не изменился


def test_months_cross_year():
    assert _months(NOW.date(), 3) == ["2026-11", "2026-12", "2027-01"]
