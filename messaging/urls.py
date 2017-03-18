from django.conf.urls import url
from messaging import views

urlpatterns = [
    url(r'^users/(?P<user_id>\w{1,300})/messages/?$', views.messages),
]