from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/?$', views.user)
    url(r'^dateslist/?$', views.dateslist)
]
