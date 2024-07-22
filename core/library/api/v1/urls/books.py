from django.urls import path
from ..views import BookListView

urlpatterns = [
    path('book/list', BookListView.as_view(), name='book_list'),
]
