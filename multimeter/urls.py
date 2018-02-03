from django.conf.urls import url
from django.contrib.auth.views import logout_then_login

from multimeter import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^account/$', views.account_view, name='account'),
    url(r'^register/$', views.register_view, name='register'),
    url(r'^password/$', views.password_view, name='password'),
]
