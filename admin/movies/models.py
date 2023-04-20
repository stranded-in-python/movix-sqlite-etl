import uuid

from .container import Container
from .enums import FilmWorkTypes, PersonRoles

models = Container.models
MinValueValidator = Container.MinValueValidator
MaxValueValidator = Container.MaxValueValidator
_ = Container.gettext_lazy


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_("Full name"), max_length=255)

    def __str__(self):
        return str(self.full_name)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")


class FilmWork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    creation_date = models.DateField(_("Creation date"))
    rating = models.FloatField(
        _("Film rating"), validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    type = models.CharField(
        _("Film type"), max_length=255, choices=FilmWorkTypes.choices
    )
    genres = models.ManyToManyField(Genre, through="FilmWorkGenre")

    def __str__(self):
        return f"{self.title} ({self.creation_date:%Y})"

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("FilmWork")
        verbose_name_plural = _("FilmWorks")


class PersonFilmWork(UUIDMixin):
    person = models.ForeignKey(
        Person, related_name="filmography", on_delete=models.CASCADE
    )
    film_work = models.ForeignKey(
        FilmWork, related_name="team", on_delete=models.CASCADE
    )
    role = models.CharField(
        _("Person's role"), max_length=20, choices=PersonRoles.choices
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _("PersonFilmWork")
        verbose_name_plural = _("PersonFilmWorks")
        unique_together = ["person_id", "film_work_id", "role"]


class FilmWorkGenre(UUIDMixin):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."film_work_genre'
        verbose_name = _("FilmWorkGenre")
        verbose_name_plural = _("FilmWorkGenres")
        unique_together = ["genre_id", "film_work_id"]
