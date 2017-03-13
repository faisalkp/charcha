from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name="home"),
    url(r'^discuss/(.*)/$', views.discussion, name="discussion"),
    url(r'^submit/$', views.submit, name="submit"),
    url(r'^profile/me/$', views.myprofile, name="myprofile"),
    url(r'^profile/(.*)/$', views.profile, name="profile"),
    url(r'^create-profile/$', views.CreateProfileView.as_view(), name="create_profile"),
    
]