import pytest

from concerts.taste import parse_artists

CSV = """﻿title,artist,album,year,rating
"The Killing Moon","Echo & the Bunnymen","Bring On the Dancing Horses",1985,8
"Allegro, Concerto in G Major","Antonio Vivaldi","La Stravaganza",1712,6
Glömd,Koop,"Sons of Koop",1997,9
"Koop Island Blues",Koop,"Koop Islands",2006,7
"Some Song",Nobody,"Album",2000,3
"""


def test_artist_rating_is_max_of_songs():
    by_name = {a.name: a.rating for a in parse_artists(CSV, min_rating=1)}
    assert by_name["Koop"] == 9


def test_commas_and_ampersands_inside_quotes():
    names = [a.name for a in parse_artists(CSV, min_rating=1)]
    assert "Echo & the Bunnymen" in names
    assert "Antonio Vivaldi" in names


def test_min_rating_and_order():
    assert [a.name for a in parse_artists(CSV, min_rating=6)] == [
        "Koop",
        "Echo & the Bunnymen",
        "Antonio Vivaldi",
    ]


def test_unexpected_header_is_an_error():
    # Python: pytest.raises — аналог expect(() => ...).toThrow()
    with pytest.raises(ValueError):
        parse_artists("foo,bar\n1,2\n", min_rating=1)
