from django.urls import path, include
from .views import SearcherView

urlpatterns = [
    path("top3/", SearcherView.as_view()),
]