from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class RoleInline(admin.TabularInline):
    model = PersonFilmWork


class GenreInline(admin.TabularInline):
    model = GenreFilmWork


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (RoleInline, GenreInline)

    list_display = ("title", "type", "creation_date", "rating")
    list_filter = ("type", "rating", "genres")
    search_fields = ("title", "description", "id")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created", "modified")
    search_fields = ("name", "description", "id")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "created", "modified")
    search_fields = ("full_name", "id")
