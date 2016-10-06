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
    asset_image = models.ImageField(upload_to = 'images/temp', max_length=255, null=True, blank=True)
    asset_details = models.TextField(blank=True)
    asset_manufacturer = models.CharField(max_length=255, blank=True)
    asset_model = models.CharField(max_length=255, blank=True)
    asset_serial_number = models.CharField(max_length=255, blank=True)
    asset_status = models.IntegerField(choices=ASSET_STATUS, default=1)
    person_responsible = models.CharField(max_length=100)
    person_responsible_email = models.EmailField()
    requires_safety_checks = models.BooleanField()
    requires_environmental_checks = models.BooleanField()
    requires_planned_maintenance = models.BooleanField()
    requires_calibration = models.BooleanField()
    calibration_date_prev = models.DateField(null=True, blank=True)
    calibration_date_next = models.DateField(null=True, blank=True)
    calibration_instructions = models.FileField(upload_to = 'files/calibration_instructions/temp', max_length=255, null=True, blank=True)
    asset_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    purchase_order_ref = models.CharField(max_length=15, blank = True)
    funded_by = models.CharField(max_length=255, blank=True)
    acquired_on = models.DateTimeField(null=True, blank=True)
    related_to_other_asset = models.ForeignKey('self', blank=True, null=True)
    asset_location_building = models.CharField(max_length=5, choices=BUILDINGS, blank=True)
    asset_location_room = models.CharField(max_length=255, blank=True)
    edited_by = models.ForeignKey("auth.User")
    edited_on = models.DateTimeField(default=timezone.now)

    def save( self, *args, **kwargs ):
        # Need custom save function to generate an asset ID / PK before the files are renamed
        # Call save first, to create a primary key
        super( Asset, self ).save( *args, **kwargs )
    
        asset_image = self.asset_image
        if asset_image:
            # If  have an image then create new filename using primary key / asset_ID and file extension
            oldfile = self.asset_image.name
            lastdot = oldfile.rfind( '.' )
            newfile = 'images/' + str( self.pk ) + oldfile[lastdot:]
    
            # Create new file and remove old one
            if newfile != oldfile:
                self.asset_image.storage.delete( newfile )
                self.asset_image.storage.save( newfile, asset_image )
                self.asset_image.name = newfile 
                self.asset_image.close()
                self.asset_image.storage.delete( oldfile )
    
        calibration_instructions = self.calibration_instructions
        if calibration_instructions:
            # If  have an image then create new filename using primary key / asset_ID and file extension
            oldfile = self.calibration_instructions.name
            lastslash = oldfile.rfind( '/' )
            newfile = 'files/calibration_instructions/' + str( self.pk ) + oldfile[lastslash:]
    
            # Create new file and remove old one
            if newfile != oldfile:
                self.calibration_instructions.storage.delete( newfile )
                self.calibration_instructions.storage.save( newfile, calibration_instructions )
                self.calibration_instructions.name = newfile 
                self.calibration_instructions.close()
                self.calibration_instructions.delete( oldfile )
    
        # Save again to keep changes
        super( Asset, self ).save( *args, **kwargs )
  
    def __str__(self):
        return self.asset_description
  
  