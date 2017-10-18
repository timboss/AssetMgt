from django.contrib import admin
from .models import (
                     Asset,
                     CalibrationRecord,
                     Buildings,
                     AmrcGroup,
                     AssetStatus,
                     EnvironmentalAspects,
                     CalibrationAssetNotificaton,
                     HighValueAssetNotification,
                     EnvironmentalAspectAssetNoficiation,
                     ArchivedAssetNotificaton,
                     QRLocation
                     )

admin.site.register(Asset)
admin.site.register(CalibrationRecord)
admin.site.register(Buildings)
admin.site.register(AmrcGroup)
admin.site.register(AssetStatus)
admin.site.register(EnvironmentalAspects)
admin.site.register(CalibrationAssetNotificaton)
admin.site.register(HighValueAssetNotification)
admin.site.register(EnvironmentalAspectAssetNoficiation)
admin.site.register(ArchivedAssetNotificaton)
admin.site.register(QRLocation)
