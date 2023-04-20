from typing import Any

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import CharField, ExpressionWrapper, Q
from django.http import JsonResponse
from django.views import generic
from movies import models
from movies.enums import PersonRoles


class MovieApiSerializerMixin:
    model = models.FilmWork

    def serialize_creation_date(self, movie: models.FilmWork) -> str:
        creation_date = str(movie.creation_date)
        if not movie.creation_date:
            creation_date = movie.created.date()  # type: ignore
        return creation_date

    def serialize_rating(self, movie: models.FilmWork) -> float:
        rating = movie.rating
        if not movie.rating:
            rating = 0.0
        return float(str(rating))

    def serialize_genres(self, movie: models.FilmWork) -> list:
        return [genre for genre in movie.list_of_genres]  # type: ignore

    def serialize_persons(
        self, movie: models.FilmWork, serialized: dict[str, Any]
    ) -> dict[str, Any]:
        serialized["actors"] = [name for name in movie.actors]  # type: ignore
        serialized["directors"] = [name for name in movie.directors]  # type: ignore
        serialized["writers"] = [name for name in movie.writers]  # type: ignore

        return serialized

    def serialize(self, movie: models.FilmWork) -> dict[str, Any]:
        if not movie:
            return {}

        serialized = {
            "id": str(movie.id),
            "title": str(movie.title),
            "description": str(movie.description) if movie.description else "",
            "creation_date": self.serialize_creation_date(movie),
            "rating": self.serialize_rating(movie),
            "type": movie.get_type_display(),  # type: ignore
            "genres": self.serialize_genres(movie),
        }
        return self.serialize_persons(movie, serialized)


class MoviesListApiView(MovieApiSerializerMixin, generic.ListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        page_num = self.request.GET.get("page")
        paginator, self.page, queryset, _ = self.paginate_queryset(
            queryset, self.paginate_by
        )

        if page_num == "first":
            page_num = 1
        if page_num == "last":
            page_num = paginator.num_pages

        page = paginator.get_page(page_num)
        context = {
            "results": [self.serialize(model) for model in page],
            "count": (paginator.count),
            "total_pages": int(paginator.num_pages),  # type: ignore
            "prev": int(page.previous_page_number()) if page.has_previous() else None,
            "next": int(page.next_page_number()) if page.has_next() else None,
        }
        return context

    def get_queryset(self):
        return (
            models.FilmWork.objects.all()  # type: ignore
            .select_related()
            .annotate(
                list_of_genres=ArrayAgg("genres__name", distinct=True),
                actors=ArrayAgg(
                    "team__person__full_name",
                    filter=ExpressionWrapper(
                        Q(team__role=PersonRoles.ACTOR), output_field=CharField()
                    ),
                ),
                writers=ArrayAgg(
                    "team__person__full_name",
                    filter=ExpressionWrapper(
                        Q(team__role=PersonRoles.WRITER), output_field=CharField()
                    ),
                ),
                directors=ArrayAgg(
                    "team__person__full_name",
                    filter=ExpressionWrapper(
                        Q(team__role=PersonRoles.DIRECTOR), output_field=CharField()
                    ),
                ),
            )
            .order_by("created", "id")
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.get_context_data())


class MovieApiView(MovieApiSerializerMixin, generic.DetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        return self.serialize(queryset.first())

    def get_queryset(self):
        movie_id = self.kwargs.get("pk")
        return (
            models.FilmWork.objects.filter(pk=movie_id)  # type: ignore
            .select_related()
            .annotate(
                list_of_genres=ArrayAgg("genres__name", distinct=True),
                actors=ArrayAgg(
                    "team__person__full_name", filter=Q(team__role=PersonRoles.ACTOR)
                ),
                writers=ArrayAgg("team__person__full_name"),
                filter=Q(team__role=PersonRoles.WRITER),
                directors=ArrayAgg(
                    "team__person__full_name", filter=Q(team__role=PersonRoles.DIRECTOR)
                ),
            )
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.get_context_data())
