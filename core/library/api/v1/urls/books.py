from django.urls import path
from .. import views

urlpatterns = [
    path('book/list/', views.BookListAPIView.as_view(), name='book_list'),
    path('suggest-by-genre/', views.GenreBasedBookSuggestionAPIView.as_view(), name='suggest-by-genre'),
    path('suggest-by-author/', views.AuthorBasedBookSuggestionAPIView.as_view(), name='suggest-by-author'),
    path('suggest-by-related-users/', views.RelatedUsersBookSuggestionAPIView.as_view(), name='suggest-by-related-users'),
]
