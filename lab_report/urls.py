from django.urls import path
from .views import *

urlpatterns = [
    path("generateLabReport", GenerateLabReport.as_view(), name="generateLabReport"),
]