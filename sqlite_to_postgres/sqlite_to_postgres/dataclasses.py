from abc import ABC
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Sequence, cast
from uuid import UUID

from dateutil import parser


def unify_datetime(field: str | datetime) -> datetime:
    if type(field) is str:
        new_datetime = parser.isoparse(field)
        return new_datetime
    return cast(datetime, field)


class Item(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()


@dataclass(slots=True)
class Person(Item):
    id: UUID
    full_name: str
    created: datetime
    modified: datetime

    def __post_init__(self):
        self.created = unify_datetime(self.created)
        self.modified = unify_datetime(self.modified)


@dataclass(slots=True)
class Genre(Item):
    id: UUID
    name: str
    description: str = field(default="")
    created: datetime = field(default=datetime.now())
    modified: datetime = field(default=datetime.now())

    def __post_init__(self):
        self.created = unify_datetime(self.created)
        self.modified = unify_datetime(self.modified)


@dataclass(slots=True)
class PersonFilmWork(Item):
    id: UUID
    person_id: UUID
    film_work_id: UUID
    role: str
    created: datetime

    def __post_init__(self):
        self.created = unify_datetime(self.created)


@dataclass(slots=True)
class GenreFilmWork(Item):
    id: UUID
    genre_id: UUID
    film_work_id: UUID
    created: datetime

    def __post_init__(self):
        self.created = unify_datetime(self.created)


@dataclass(slots=True)
class FilmWork(Item):
    id: UUID
    title: str
    description: str
    creation_date: date
    rating: float
    type: str
    created: datetime
    modified: datetime

    def __post_init__(self):
        self.created = unify_datetime(self.created)
        self.modified = unify_datetime(self.modified)
        if not self.creation_date:
            self.creation_date = self.created.date()
        if not self.rating:
            self.rating = 0.0


@dataclass(slots=True)
class MoviesData:
    persons: Sequence[Item]
    genres: Sequence[Item]
    film_works: Sequence[Item]
    person_film_works: Sequence[Item]
    genre_film_works: Sequence[Item]
