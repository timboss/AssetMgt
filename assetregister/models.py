from django.db import models
from django.utils import timezone
import os
from haystack.management.commands import update_index, rebuild_index


BUILDINGS = (
    ("Rolls-Royce Factory of the Future (8306)", "Rolls-Royce Factory of the Future (8306)"),
    ("Factory 2050 (8324)", "Factory 2050 (8324)"),
    ("Design, Prototyping & Testing Centre (8304)", "Design, Prototyping & Testing Centre (8304)"),
    ("Nuclear AMRC (8307)", "Nuclear AMRC (8307)"),
    ("Knowledge Transfer Centre (8313)", "Knowledge Transfer Centre (8313)"),
    ("AMRC Training Centre (8320)", "AMRC Training Centre (8320)"),
    ("Castings Technology International 1 (Waverly 1) (8322)", "Castings Technology International 1 (Waverly 1) (8322)"),
    ("Castings Foundry of the Future (Waverly 2) (8323)", "Castings Foundry of the Future (Waverly 2) (8323)"),
)

ASSET_STATUS = (
    ("Active / In-Use", "Active / In-Use"),
    ("Inactive (Being Comissioned / Repaired)", "Inactive (Being Comissioned / Repaired)"),
    ("Quarantined", "Quarantined"),
    ("Decomissioned / Withdrawn", "Decomissioned / Withdrawn"),
    ("Archived", "Archived"),
)

class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_description = models.CharField(max_length=200)
    asset_image = models.ImageField(upload_to = "images/temp", max_length=255, null=True, blank=True)
    asset_image_thumbnail = models.ImageField(upload_to = "images", editable=False, null=True)
    asset_details = models.TextField(blank=True)
    asset_manufacturer = models.CharField(max_length=255, blank=True)
    asset_model = models.CharField(max_length=255, blank=True)
    asset_serial_number = models.CharField(max_length=255, blank=True)
    asset_status = models.CharField(max_length=100, choices=ASSET_STATUS, default="Active / In-Use")
    person_responsible = models.CharField(max_length=100)
    person_responsible_email = models.EmailField()
    requires_insurance = models.BooleanField()
    requires_safety_checks = models.BooleanField()
    requires_environmental_checks = models.BooleanField()
    requires_planned_maintenance = models.BooleanField()
    maintenance_instructions = models.URLField(max_length=255, null=True, blank=True)
    requires_calibration = models.BooleanField()
    calibration_date_prev = models.DateField(null=True, blank=True)
    calibration_date_next = models.DateField(null=True, blank=True)
    calibration_instructions = models.URLField(max_length=255, null=True, blank=True)
    asset_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    purchase_order_ref = models.CharField(max_length=15, blank = True)
    funded_by = models.CharField(max_length=255, blank=True)
    acquired_on = models.DateTimeField(null=True, blank=True)
    related_to_other_asset = models.ForeignKey("self", blank=True, null=True)
    asset_location_building = models.CharField(max_length=128, choices=BUILDINGS, blank=True)
    asset_location_room = models.CharField(max_length=255, blank=True)
    edited_by = models.ForeignKey("auth.User")
    edited_on = models.DateTimeField(default=timezone.now)

    def save( self, *args, **kwargs ):
        # Custom save function to generate an asset ID / PK needed to rename files, move and rename image upload and create thumbnail
        
        # Call save first, to create a primary key
        super( Asset, self ).save( *args, **kwargs )
    
        # Check if have any asset image (newly uploaded, or kept from previous upload)
        asset_image = self.asset_image
        if asset_image:
            
            # If have an uploaded image then import the things needed to make watermark & thumbnail
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage as storage
            from io import BytesIO
            from PIL import Image, ImageEnhance
            
            # Create image filename using pk / asset_ID and original file extension
            oldfile = self.asset_image.name
            lastdot = oldfile.rfind(".")
            newfile = "images/" + str( self.pk ) + oldfile[lastdot:]
            
            # Create image with new filename, remove old image if "filepath" (really only file extension!) is now different
            if newfile != oldfile:
                self.asset_image.storage.delete( newfile )
                self.asset_image.storage.save( newfile, asset_image )
                self.asset_image.name = newfile 
                self.asset_image.close()
                self.asset_image.storage.delete( oldfile )
                
            oldthumbnail = self.asset_image_thumbnail
            if oldthumbnail:
                # Delte old thumb
                oldthumbname = self.asset_image_thumbnail.name
                self.asset_image_thumbnail.storage.delete( oldthumbname )
                            
            # Save changes    
            super( Asset, self ).save( *args, **kwargs )
            
            
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
            logoimage = storage.open("images/watermarklogo.png")
            img = Image.open(assetimage).convert("RGBA")
            logo = Image.open(logoimage).convert("RGBA")
            
            img_w = img.size[0]
            img_h = img.size[1]

            # resize logo to be quarter of asset_image width, but same aspect ratio!        
            logo_aspect_ratio = float(logo.size[0] / logo.size[1])
            
            # Resize logo to be half (if image width <= 300) else 5th of image's shortest side
            if img_w > img_h:
                if img_w <= 300: 
                    logo_w = int(img_w / 2) 
                else:  
                    logo_w = int(img_w / 5)
                logo_h = int(logo_w / logo_aspect_ratio)
            else:
                if img_h <= 300: 
                    logo_h = int(img_h / 2) 
                else:  
                    logo_h = int(img_h / 5)
                logo_w = int(logo_h * logo_aspect_ratio)
        
            logo = logo.resize((logo_w, logo_h), Image.ANTIALIAS)
        
            # position the watermark centrally
            offset_x = ((img.size[0]) / 2) - ((logo.size[0]) / 2)
            offset_y = ((img.size[1]) / 2) - ((logo.size[1]) / 2)
        
            watermark = Image.new("RGBA", img.size, (255, 255, 255, 1))
            watermark.paste(logo, (int(offset_x), int(offset_y)), mask=logo.split()[3])
        
            alpha = watermark.split()[3]
            #alpha = ImageEnhance.Brightness(alpha) #.enhance(opacity) # NameError "opacity" not defined
        
            watermark.putalpha(alpha)
            Image.composite(watermark, img, watermark).save("media/" + self.asset_image.name, "JPEG")
        
        else:
            # Have no image now, so delete any old thumbnail & update DB
            oldthumbname = self.asset_image_thumbnail.name
            if oldthumbname:
                self.asset_image_thumbnail.storage.delete( oldthumbname )
                self.asset_image_thumbnail = None
    
        # Attempt to update Whoosh index when new asset added. 
        # Need to move this to an async message queue ASAP, currently takes 10-15 seconds to reindex ~15 assets!
        update_index.Command().handle(interactive=False, remove=True)
    
        # Save again to keep changes
        super( Asset, self ).save( *args, **kwargs )
               
        
    def get_absolute_url(self):
        return "/asset/%i/" % self.asset_id
  
    def __str__(self):
        return self.asset_description
  
  