from django.contrib import admin
from .models import Asset, CalibrationRecord, Buildings, AssetStatus, EnviroAspects, EmailsTo
# Register your models here.

admin.site.register(Asset)
admin.site.register(CalibrationRecord)
admin.site.register(Buildings)
admin.site.register(AssetStatus)
admin.site.register(EnviroAspects)
admin.site.register(EmailsTo)
