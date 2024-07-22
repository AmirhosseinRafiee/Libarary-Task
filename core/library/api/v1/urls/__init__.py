from django.urls import path, include

urlpatterns = [
    path('', include('library.api.v1.urls.books')),
    path('', include('library.api.v1.urls.reviews')),
]
