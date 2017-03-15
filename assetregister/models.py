from django.db import models
from django.utils import timezone
from django.conf import settings
import os
from haystack.management.commands import update_index
import logging
import uuid
from background_task import background

logger = logging.getLogger(__name__)

default_asset_status = 1

@background()
def reindex_whoosh():
    update_index.Command().handle(interactive=False, remove=True, age=1)
    # age=1 will only add assets edited in last hour.
    # need separate task to reindex whole db each night (will remove orphans)

class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_description = models.CharField(max_length=200)
    asset_image = models.ImageField(upload_to="images/temp", max_length=255, null=True, blank=True)
    asset_image_thumbnail = models.ImageField(upload_to="images", editable=False, null=True)
    asset_details = models.TextField(blank=True)
    asset_manufacturer = models.CharField(max_length=255, blank=True)
    asset_model = models.CharField(max_length=255, blank=True)
    asset_serial_number = models.CharField(max_length=255, null=True, blank=True)
    amrc_equipment_id = models.CharField(max_length=16, null=True, blank=True)
    handling_and_storage_instructions = models.URLField(max_length=255, null=True, blank=True)
    operating_instructions = models.URLField(max_length=255, null=True, blank=True)
    asset_status = models.ForeignKey("AssetStatus", on_delete=models.SET_NULL, null=True, default=default_asset_status, related_name="status")
    person_responsible = models.CharField(max_length=100)
    person_responsible_email = models.EmailField()
    requires_insurance = models.BooleanField()
    requires_safety_checks = models.BooleanField()
    safety_notes = models.TextField(blank=True)
    requires_environmental_checks = models.BooleanField()
    environmental_aspects = models.ManyToManyField("EnvironmentalAspects", blank=True)
    environmental_notes = models.TextField(blank=True)
    emergency_response_information = models.TextField(blank=True)
    requires_planned_maintenance = models.BooleanField()
    maintenance_instructions = models.URLField(max_length=255, null=True, blank=True)
    maintenance_records = models.URLField(max_length=255, null=True, blank=True)
    maintenance_notes = models.TextField(blank=True)
    requires_calibration = models.BooleanField()
    calibration_frequency = models.CharField(max_length=64, null=True, blank=True)
    passed_calibration = models.BooleanField(default=False)
    calibration_date_prev = models.DateField(null=True, blank=True)
    calibration_date_next = models.DateField(null=True, blank=True)
    calibration_instructions = models.URLField(max_length=255, null=True, blank=True)
    asset_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    charge_out_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    charge_code = models.CharField(max_length=64, null=True, blank=True)
    purchase_order_ref = models.CharField(max_length=15, blank=True)
    funded_by = models.CharField(max_length=255, blank=True)
    acquired_on = models.DateField(null=True, blank=True)
    disposal_date = models.DateField(null=True, blank=True)
    disposal_method = models.CharField(max_length=255, null=True, blank=True)
    parent_assets = models.ManyToManyField("self", blank=True)
    asset_location_building = models.ForeignKey("Buildings", on_delete=models.SET_NULL, blank=True, null=True, related_name="building")
    asset_location_room = models.CharField(max_length=255, blank=True)
    edited_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    edited_on = models.DateTimeField(default=timezone.now)
    
    def image_move_rename():
        pass
    
    def image_thumbnail():
        pass 
   
    def image_watermark():
        pass
    
    def save(self, *args, **kwargs):
        # Custom save function to generate an asset ID / PK needed to rename files,_
        # move and rename image upload and create thumbnail

        # Call save first, to create a primary key
        super(Asset, self).save(*args, **kwargs)

        # Check if have any asset image (newly uploaded, or kept from previous upload)
        asset_image = self.asset_image
        if asset_image:

            # If asset_image.name contains "/temp" then it's newly uploaded so rename, move, thumbnail and watermark
            if "images/temp" in self.asset_image.name:
                
                # !!!
                # image_move_rename()
                # image_thumbnail()
                # image_watermark()
                # !!!

                # If have a newly uploaded image then import the things needed to make watermark & thumbnail
                from django.core.files.base import ContentFile
                from django.core.files.storage import default_storage as storage
                from io import BytesIO
                from PIL import Image

                # Create image filename using pk / asset_ID and original file extension
                oldfile = self.asset_image.name
                lastdot = oldfile.rfind(".")
                newfile = "images/" + str(self.pk) + oldfile[lastdot:]

                # Create image with new filename, remove old image if "filepath"_
                # (really only file extension!) is now different
                if newfile != oldfile:
                    self.asset_image.storage.delete(newfile)
                    self.asset_image.storage.save(newfile, asset_image)
                    self.asset_image.name = newfile
                    self.asset_image.close()
                    self.asset_image.storage.delete(oldfile)

                oldthumbnail = self.asset_image_thumbnail
                if oldthumbnail:
                    # Delte old thumb
                    oldthumbname = self.asset_image_thumbnail.name
                    self.asset_image_thumbnail.storage.delete(oldthumbname)

                # Save changes
                super(Asset, self).save(*args, **kwargs)

                # -- THUMBNAIL --
                THUMB_SIZE = (300, 200)

                # Open image to thumbnail
                fh = storage.open(self.asset_image.name)
                image = Image.open(fh)

                image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
                fh.close()

                thumb_name, thumb_extension = os.path.splitext(self.asset_image.name)
                thumb_extension = thumb_extension.lower()
                thumb_filename = thumb_name + "_thumb" + thumb_extension

                if thumb_extension in [".jpg", ".jpeg"]:
                    FTYPE = "JPEG"
                elif thumb_extension == ".gif":
                    FTYPE = "GIF"
                elif thumb_extension == ".png":
                    FTYPE = "PNG"
                else:
                    raise Exception("Error creating thumnail. Image must be a .jpg, .jpeg, .gif or .png!")

                temp_thumb = BytesIO()
                image.save(temp_thumb, FTYPE, quality=100)
                temp_thumb.seek(0)
                self.asset_image_thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
                temp_thumb.close()

                # -- WATERMARK --
                assetimage = storage.open(self.asset_image.name)
                logoimage = storage.open("images/watermarklogo4.png")
                img = Image.open(assetimage).convert("RGBA")
                logo = Image.open(logoimage).convert("RGBA")

                img_w = img.size[0]
                img_h = img.size[1]

                # resize logo to be quarter of asset_image width, but same aspect ratio!
                logo_aspect_ratio = float(logo.size[0] / logo.size[1])

                # If image width or height <= 400 resize logo to be half, else 1/4th of image's shortest side
                if img_w > img_h:
                    if img_w <= 400:
                        logo_w = int(img_w / 2)
                    else:
                        logo_w = int(img_w / 4)
                    logo_h = int(logo_w / logo_aspect_ratio)
                else:
                    if img_h <= 400:
                        logo_h = int(img_h / 2)
                    else:
                        logo_h = int(img_h / 4)
                    logo_w = int(logo_h * logo_aspect_ratio)

                logo = logo.resize((logo_w, logo_h), Image.ANTIALIAS)

                # position the watermark centrally
                offset_x = ((img.size[0]) / 2) - ((logo.size[0]) / 2)
                offset_y = ((img.size[1]) / 2) - ((logo.size[1]) / 2)

                watermark = Image.new("RGBA", img.size, (255, 255, 255, 1))
                watermark.paste(logo, (int(offset_x), int(offset_y)), mask=logo.split()[3])

                alpha = watermark.split()[3]
                # alpha = ImageEnhance.Brightness(alpha).enhance(opacity) # NameError on "opacity"

                watermark.putalpha(alpha)
                Image.composite(watermark, img, watermark).save("media/" + self.asset_image.name, "JPEG")

        else:
            # Have no image now, delete any old thumbnail & update DB
            oldthumbname = self.asset_image_thumbnail.name
            if oldthumbname:
                self.asset_image_thumbnail.storage.delete(oldthumbname)
                self.asset_image_thumbnail = None

        # Update Whoosh index (via async task queue) when new asset added.
        reindex_whoosh()

        # Save again to keep all changes
        super(Asset, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/asset/%i/" % self.asset_id

    def __str__(self):
        if not self.asset_manufacturer:
            return "{} - {}".format(self.asset_id, self.asset_description)
        else:
            return "{} - {} - {}".format(self.asset_id, self.asset_manufacturer, self.asset_description)


CALIBRATION_OUTCOME = (
                       ("Pass", "Pass"),
                       ("Fail", "Fail")
                     )


class CalibrationRecord(models.Model):
    calibration_record_id = models.AutoField(primary_key=True)
    slug = models.CharField(max_length=64, blank=True, null=True, unique=True)
    asset = models.ForeignKey("assetregister.Asset", on_delete=models.CASCADE, related_name="calibration", limit_choices_to={'requires_calibration': True})
    calibration_description = models.CharField(max_length=200)
    calibration_date = models.DateField(default=timezone.now)
    calibration_date_next = models.DateField(null=True, blank=True)
    calibrated_by_internal = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="calibrator")
    calibrated_by_external = models.CharField(max_length=200, null=True, blank=True)
    calibration_outcome = models.CharField(max_length=10, choices=CALIBRATION_OUTCOME, default="Pass")
    calibration_notes = models.TextField(null=True, blank=True)
    calibration_certificate = models.URLField(max_length=255, null=True, blank=True)
    calibration_entered_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    calibration_entered_on = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return "/calibrationrecord/{}/".format(self.calibration_record_id)

    def __str__(self):
        return "Calibration #{} - {} - {}".format(self.pk, self.asset, self.calibration_description)

    def save(self, *args, **kwargs):

        super(CalibrationRecord, self).save(*args, **kwargs)

        # Check if this is the latest calibration record for any asset, if so update asset.calibration_dates and status
        latest_asset_calibration = CalibrationRecord.objects.filter(asset=self.asset.pk).order_by("-calibration_date", "-calibration_record_id")[0]

        if self.pk == latest_asset_calibration.pk:

            Asset.objects.filter(pk=self.asset.asset_id).update(calibration_date_prev=self.calibration_date)

            if self.calibration_date_next:
                Asset.objects.filter(pk=self.asset.asset_id).update(calibration_date_next=self.calibration_date_next)
            else:
                Asset.objects.filter(pk=self.asset.asset_id).update(calibration_date_next=None)

            if self.calibration_outcome == "Pass":
                Asset.objects.filter(pk=self.asset.asset_id).update(passed_calibration=True)
            else:
                Asset.objects.filter(pk=self.asset.asset_id).update(passed_calibration=False)

        # If new record, generate unique slug
        if not self.slug:
            self.slug = uuid.uuid1()

        super(CalibrationRecord, self).save(*args, **kwargs)


class Buildings(models.Model):
    building_name = models.CharField(max_length=255)
    EFM_building_code = models.CharField(max_length=6)

    def __str__(self):
        return "{} ({})".format(self.building_name, self.EFM_building_code)


class AssetStatus(models.Model):
    status_name = models.CharField(max_length=255)

    def __str__(self):
        return self.status_name


class EnvironmentalAspects(models.Model):
    aspect = models.CharField(max_length=255)

    def __str__(self):
        return self.aspect


class CalibrationAssetNotificaton(models.Model):
    email_address = models.EmailField()

    def __str__(self):
        return "Notify {} of assets requiring calibration".format(self.email_address)


class HighValueAssetNotification(models.Model):
    email_address = models.EmailField()
    if_asset_value_above = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return "Notify {} of assets with value exceeding £{}".format(self.email_address, self.if_asset_value_above)


class EnvironmentalAspectAssetNoficiation(models.Model):
    email_address = models.EmailField()

    def __str__(self):
        return "Notify {} of assets with environmental aspects".format(self.email_address)
