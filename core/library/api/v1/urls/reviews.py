from django.urls import path
from ..views import AddReviewAPIView, UpdateReviewAPIView, DeleteReviewAPIView

urlpatterns = [
    path('review/add/', AddReviewAPIView.as_view(), name='add_review'),
    path('review/update/', UpdateReviewAPIView.as_view(), name='update_review'),
    path('review/delete/<int:review_id>/', DeleteReviewAPIView.as_view(), name='delete_review'),
]
