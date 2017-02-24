from django.contrib import admin
from .models import Asset, CalibrationRecord
# Register your models here.

admin.site.register(Asset)
admin.site.register(CalibrationRecord)
