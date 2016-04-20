from django import forms
from .models import Asset


class EditAsset(forms.ModelForm):  
    class Meta:
        model = Asset
        fields =  [
            "asset_description", "asset_image", "asset_details", "asset_manufacturer", "asset_model", "asset_serial_number", "asset_status",
            "person_responsible", "person_responsible_email", "requires_calibration", "requires_safetychecks", "requires_environmentalchecks",
            "requires_plannedmaintenance", "calibration_instructions", "asset_value", "purchase_order_ref", "funded_by", "acquired_on",
            "related_to_other_asset", "asset_location_building", "asset_location_room",
            ]