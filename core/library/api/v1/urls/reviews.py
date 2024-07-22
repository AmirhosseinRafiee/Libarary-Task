from django.urls import path
from ..views import AddReviewView, UpdateReviewView, DeleteReviewView

urlpatterns = [
    path('review/add/', AddReviewView.as_view(), name='add_review'),
    path('review/update/', UpdateReviewView.as_view(), name='update_review'),
    path('review/delete/<int:review_id>/', DeleteReviewView.as_view(), name='delete_review'),
]
