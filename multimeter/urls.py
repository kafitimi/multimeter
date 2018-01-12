from django.conf.urls import url
from multimeter import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
]
