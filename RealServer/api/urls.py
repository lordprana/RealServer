from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/?$', views.users),
    url(r'^users/(?P<user_id>\w{1,50})/$', views.user),
    url(r'^users/(?P<user_id>\w{1,50})/dateslist/?$', views.dateslist)
]
