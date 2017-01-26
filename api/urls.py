from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/?$', views.users),
    url(r'^users/(?P<user_id>\w{1,50})/?$', views.user),
    url(r'^users/(?P<user_id>\w{1,50})/date/?$', views.date),
    url(r'^users/(?P<user_id>\w{1,50})/dates/(?P<date_id>\w{1,50})/?$', views.date),
    url(r'^users/(?P<user_id>\w{1,50})/sign_s3/?$', views.sign_s3),
    url(r'^users/(?P<user_id>\w{1,50})/past_dates/?$', views.past_dates),
    url(r'reportandblock/?$', views.report_and_block)
]
