from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/?$', views.users),
    url(r'^fake_users/?$', views.fake_users),
    url(r'^users/(?P<user_id>\w{1,300})/?$', views.user),
    url(r'^users/(?P<user_id>\w{1,300})/time_preferences/?$', views.get_time_preferences),
    url(r'^users/(?P<user_id>\w{1,300})/place_preferences/?$', views.get_place_preferences),
    url(r'^users/(?P<user_id>\w{1,300})/date/?$', views.date),
    url(r'^users/(?P<user_id>\w{1,300})/dates/(?P<date_id>\w{1,50})/?$', views.date),
    url(r'^users/(?P<user_id>\w{1,300})/dates/(?P<date_id>\w{1,50})/unmatch/?$', views.unmatch),
    url(r'^users/(?P<user_id>\w{1,300})/dates/(?P<date_id>\w{1,50})/check_date_location/?$', views.check_date_location),
    url(r'^users/(?P<user_id>\w{1,300})/settings/?$', views.settings),
    url(r'^users/(?P<user_id>\w{1,300})/logout/?$', views.logout),
    url(r'^users/(?P<user_id>\w{1,300})/sign_s3/?$', views.sign_s3),
    url(r'^users/(?P<user_id>\w{1,300})/past_dates/?$', views.past_dates),
    url(r'^users/(?P<user_id>\w{1,300})/register_device/?$', views.register_fcm_device),
    url(r'reportandblock/?$', views.report_and_block)
]
