from django.urls import path

from apps.pinger.views import Pinger

urlpatterns = [
    path("", Pinger.as_view(), name="pinger"),
    path("<int:network_id>/", Pinger.as_view(), name="pinger"),
]
