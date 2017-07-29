from django.conf.urls import url, include
from django.contrib.auth.views import logout_then_login
from multimeter import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
]
