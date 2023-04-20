from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy


class Container:
    """Class used as dependency injection"""

    models = models
    gettext_lazy = gettext_lazy
    MinValueValidator = MinValueValidator
    MaxValueValidator = MaxValueValidator
