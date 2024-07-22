from django.urls import path, include

app_name = 'library'

urlpatterns = [
    path('api/v1/', include('library.api.v1.urls'))
]
