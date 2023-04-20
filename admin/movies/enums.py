from .container import Container

models = Container.models
_ = Container.gettext_lazy


class FilmWorkTypes(models.TextChoices):
    MOVIE = "movie", _("Movie")
    SERIES = "tv_show", _("Series")


class PersonRoles(models.TextChoices):
    ACTOR = "actor", _("Actor")
    DIRECTOR = "director", _("Director")
    WRITER = "writer", _("Writer")
