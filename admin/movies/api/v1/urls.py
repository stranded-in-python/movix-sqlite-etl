from django.urls import path

from .views import MovieApiView, MoviesListApiView

urlpatterns = [
    path("movies/", MoviesListApiView.as_view(), name="movies"),
    path("movies/<uuid:pk>/", MovieApiView.as_view(), name="movie-detail"),
]
