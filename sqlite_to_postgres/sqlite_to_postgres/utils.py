from dataclasses import fields

from .dataclasses import (
    FilmWork,
    Genre,
    GenreFilmWork,
    Item,
    MoviesData,
    Person,
    PersonFilmWork,
)


def is_data_empty(data: MoviesData) -> bool:
    return not any(
        [
            data.persons,
            data.genres,
            data.film_works,
            data.person_film_works,
            data.genre_film_works,
        ]
    )


def map_name(name: str, mapping: dict[str, str]) -> str:
    return name if not mapping.get(name) else str(mapping.get(name))


def get_field_names(item: type[Item], mapping: dict[str, str]) -> list[str]:
    return [map_name(f.name, mapping) for f in fields(item)]


def get_table_fields(
    table: str, item: type[Item], mapping: dict[str, str]
) -> list[str]:
    table_name = map_name(table, mapping)
    return [f"{table_name}.{f}" for f in get_field_names(item, mapping)]


def get_schema_table_name(table: str, schema: str, mapping: dict[str, str]):
    if not schema:
        return table
    return f"{schema}.{map_name(table, mapping)}"


def get_mapping(
    name_mapping: dict[str, str], schema: str
) -> dict[str, tuple[type[Item], dict[str, str], str]]:
    return {
        "person": (Person, name_mapping, schema),
        "genre": (Genre, name_mapping, schema),
        "film_work": (FilmWork, name_mapping, schema),
        "person_film_work": (PersonFilmWork, name_mapping, schema),
        "genre_film_work": (GenreFilmWork, name_mapping, schema),
    }


class SQLBuilderDataclassMixin:
    table: str
    item: type[Item]
    schema: str
    name_mapping: dict[str, str]

    @property
    def full_table_name(self):
        return get_schema_table_name(self.table, self.schema, self.name_mapping)

    @property
    def table_name(self):
        return map_name(self.table, self.name_mapping)

    @property
    def table_fields(self):
        return ", ".join(get_table_fields(self.table, self.item, self.name_mapping))

    @property
    def fields(self):
        return ", ".join(get_field_names(self.item, self.name_mapping))

    @property
    def placeholders(self):
        placeholders = ["%s" for _ in get_field_names(self.item, self.name_mapping)]
        return ", ".join(placeholders)
