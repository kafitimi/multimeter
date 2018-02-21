from django.contrib import admin
from . import models


admin.site.register(models.CountryReference)
admin.site.register(models.Account)
admin.site.register(models.Contest)
admin.site.register(models.Task)
admin.site.register(models.ContestTask)
admin.site.register(models.SubTask)
admin.site.register(models.Language)
