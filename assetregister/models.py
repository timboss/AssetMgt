from django.db import models
from django.utils import timezone
import os
from uuid import uuid4


def img_path_and_rename(instance, filename):
    upload_to = 'images'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

def calibration_instructions_path_and_rename(instance, filename):
    upload_to = 'files/calibration_instructions'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


BUILDINGS = (
    ("FOF", "Rolls-Royce Factory of the Future (8306)"),
    ("2050", "Factory 2050 (8324)"),
    ("DPTC", "Design, Prototyping & Testing Centre (8304)"),
    ("NAMRC", "Nuclear AMRC (8307)"),
    ("KTC", "Knowledge Transfer Centre (8313)"),
    ("TC", "AMRC Training Centre (8320)"),
    ("CTI", "Castings Technology International 1 (Waverly 1) (8322)"),
    ("WAV2", "Castings Foundry of the Future (Waverly 2) (8323)"),
)

ASSET_STATUS = (
    (1, "Active / In-Use"),
    (2, "Inactive (Being Comissioned / Repaired)"),
    (3, "Quarantined"),
    (4, "Decomissioned / Withdrawn"),
)

class Asset(models.Model):
  asset_id = models.AutoField(primary_key=True)
  asset_description = models.CharField(max_length=200)
  asset_image = models.ImageField(upload_to = img_path_and_rename, max_length=255, null=True, blank=True)
  asset_details = models.TextField(blank=True)
  asset_manufacturer = models.CharField(max_length=255, blank=True)
  asset_model = models.CharField(max_length=255, blank=True)
  asset_serial_number = models.CharField(max_length=200, blank=True)
  asset_status = models.IntegerField(choices=ASSET_STATUS, default=1)
  person_responsible = models.CharField(max_length=100)
  person_responsible_email = models.EmailField()
  requires_calibration = models.BooleanField()
  requires_safetychecks = models.BooleanField()
  requires_environmentalchecks = models.BooleanField()
  requires_plannedmaintenance = models.BooleanField()
  calibration_instructions = models.FileField(upload_to = calibration_instructions_path_and_rename, max_length=255, null=True, blank=True)
  asset_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  purchase_order_ref = models.CharField(max_length=15, blank = True)
  funded_by = models.CharField(max_length=200, blank=True)
  acquired_on = models.DateTimeField(null=True, blank=True)
  related_to_other_asset = models.ForeignKey('self', blank=True, null=True)
  asset_location_building = models.CharField(max_length=5, choices=BUILDINGS, blank=True)
  asset_location_room = models.CharField(max_length=200, blank=True)
  added_by = models.ForeignKey("auth.User")
  added_on = models.DateTimeField(default=timezone.now)
  
  def __str__(self):
      return self.asset_description
  
  