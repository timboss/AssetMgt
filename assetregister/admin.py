from django.contrib import admin
from .models import (
                     Asset,
                     CalibrationRecord,
                     Buildings,
                     AssetStatus,
                     EnvironmentalAspects,
                     CalibrationAssetNotificaton,
                     HighValueAssetNotification,
                     EnvironmentalAspectAssetNoficiation,
                     )

admin.site.register(Asset)
admin.site.register(CalibrationRecord)
admin.site.register(Buildings)
admin.site.register(AssetStatus)
admin.site.register(EnvironmentalAspects)
admin.site.register(CalibrationAssetNotificaton)
admin.site.register(HighValueAssetNotification)
admin.site.register(EnvironmentalAspectAssetNoficiation)
