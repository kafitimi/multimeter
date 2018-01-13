from django.conf.urls import url
from django.contrib.auth.views import logout_then_login

from multimeter.views import account_view, index_view, login_view, password_view

urlpatterns = [
    url(r'^$', index_view, name='index'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^account/$', account_view, name='account'),
    url(r'^password/$', password_view, name='password'),
]
