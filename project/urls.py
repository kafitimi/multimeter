from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.contrib import admin

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('multimeter.urls')),
)
