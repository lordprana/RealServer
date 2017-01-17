from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/?$', views.users),
    url(r'^users/(?P<user_id>\w{1,50})/?$', views.user),
    url(r'^users/(?P<user_id>\w{1,50})/dates/?$', views.dates),
    url(r'^users/(?P<user_id>\w{1,50})/dates/(?P<date_id>\w{1,50})/?$', views.date),
    url(r'reportandblock/?$', views.report_and_block)
]
