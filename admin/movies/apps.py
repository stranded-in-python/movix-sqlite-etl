from django.apps import AppConfig

from .container import Container

_ = Container.gettext_lazy


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "movies"
    verbose_name = _("movies")
