from django import forms
from .models import Asset, CalibrationRecord, AmrcGroup, Buildings, QRLocation, AssetStatus
from haystack.forms import HighlightedSearchForm
# from haystack.query import SearchQuerySet
from django.utils import timezone
from django.core.validators import RegexValidator
import django_filters


class DateInput(forms.DateInput):
    # if this is "date" it will clash with Chrome's built-in date picker and won't work
    input_type = "text"


class EditAsset(forms.ModelForm):
    asset_qr_location_manual = forms.IntegerField(
                                                  required=False,
                                                  label="""AMRC QR Location ID.  (Setting this will override anything in the Asset Location
                                                   Building or Specific Location or Room)""",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )
    parent_assets_manual = forms.CharField(
                                           required=False,
                                           label="Enter all Asset IDs to relate to this asset separated by commas",
                                           widget=forms.TextInput(attrs={"class": "form-control"}),
                                           validators=[
                                                       RegexValidator(
                                                                      regex="^[0-9, ]*$",
                                                                      message="Must be a list of Asset IDs (integers) separated by commas",
                                                                      code="invalid_username"
                                                                      )
                                                       ]
                                           )

    class Meta:
        model = Asset
        fields = [
            "asset_description", "person_responsible", "person_responsible_email", "amrc_group_responsible",
            "asset_image", "asset_status", "asset_details", "asset_manufacturer", "asset_model", "asset_serial_number",
            "amrc_equipment_id", "grn_id", "dispatch_note_id", "operating_instructions", "handling_and_storage_instructions",
            "requires_calibration", "requires_safety_checks", "safety_notes",
            "emergency_response_information", "requires_environmental_checks", "environmental_aspects",
            "environmental_notes", "requires_planned_maintenance", "maintenance_instructions",
            "maintenance_records", "maintenance_notes", "asset_value", "charge_out_rate", "requires_insurance",
            "requires_unforseen_damage_insurance", "purchase_order_ref", "funded_by", "acquired_on",
            "disposal_date", "disposal_method", "parent_assets", "asset_location_building", "asset_location_room",
            "asset_qr_location"
            ]
        widgets = {
            "asset_description": forms.TextInput(attrs={"class": "form-control"}),
            "asset_details": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "asset_manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "asset_model": forms.TextInput(attrs={"class": "form-control"}),
            "asset_serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "amrc_equipment_id": forms.TextInput(attrs={"class": "form-control"}),
            "asset_status": forms.Select(attrs={"class": "form-control"}),
            "person_responsible": forms.TextInput(attrs={"class": "form-control"}),
            "person_responsible_email": forms.EmailInput(attrs={"class": "form-control"}),
            "amrc_group_responsible": forms.Select(attrs={"class": "form-control"}),
            "asset_qr_location": forms.Select(attrs={"class": "form-control example-enableFiltering", "style": "width: 400px;"}),
            "safety_notes": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "environmental_aspects": forms.CheckboxSelectMultiple(),
            "environmental_notes": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "emergency_response_information": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "maintenance_instructions": forms.URLInput(attrs={"class": "form-control"}),
            "maintenance_records": forms.URLInput(attrs={"class": "form-control"}),
            "maintenance_notes": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "asset_value": forms.TextInput(attrs={"class": "form-control"}),
            "charge_out_rate": forms.TextInput(attrs={"class": "form-control"}),
            "purchase_order_ref": forms.TextInput(attrs={"class": "form-control"}),
            "grn_id": forms.TextInput(attrs={"class": "form-control"}),
            "funded_by": forms.TextInput(attrs={"class": "form-control"}),
            "acquired_on": DateInput(attrs={"class": "datepicker form-control"}),
            "disposal_date": DateInput(attrs={"class": "datepicker form-control"}),
            "disposal_method": forms.TextInput(attrs={"class": "form-control"}),
            "dispatch_note_id": forms.TextInput(attrs={"class": "form-control"}),
            "parent_assets": forms.SelectMultiple(attrs={"class": "form-control example-enableFiltering", "style": "width: 400px;"}),
            "asset_location_building": forms.Select(attrs={"class": "form-control"}),
            "asset_location_room": forms.TextInput(attrs={"class": "form-control"}),
            "operating_instructions": forms.URLInput(attrs={"class": "form-control"}),
            "handling_and_storage_instructions": forms.URLInput(attrs={"class": "form-control"}),
        }
        labels = {
          "asset_description": ("Asset Description* "),
          "assset_details": ("Asset Details or Notes"),
          "person_responsible": ("Person Responsible* "),
          "person_responsible_email": ("Person Responsible Email* "),
          "asset_image": ("""Asset Image (All AMRC staff can currently see all asset images,
           ensure nothing sensitive is visible in the image before uploading!)"""),
          "parent_assets": ("Related Assets"),
          "amrc_equipment_id": ("Existing Engraved AMRC Equipment ID (e.g. V112 or M206B)"),
          "asset_location_room": ("Asset Location (e.g. Specific area, room or shelf etc.)"),
          "maintenance_instructions": ("Maintenance Instructions URL"),
          "maintenance_records": ("Maintenance Records URL"),
          "operating_instructions": ("Operating Instructions URL"),
          "handling_and_storage_instructions": ("Handling and Storage Instructions URL"),
          "asset_value": ("Asset Value £"),
          "charge_out_rate": ("Charge Out Rate £"),
          "grn": ("AMRC Goods Received Note [GRN] ID (e.g. GRN.1234)"),
          "dispatch_note": ("AMRC Dispatch Note [DN] ID (e.g. DN.1234)"),
          "environmental_aspects": ("Environmental Aspects (please tick all that apply)"),
          "grn_id": ("AMRC Goods Received Note [GRN] ID"),
          "dispatch_note_id": ("AMRC Dispatch Note [DN] ID"),
          "asset_qr_location": ("""AMRC QR Location ID.  (Setting this will overwrite anything in the "Asset Location
                                 Building" or "Asset Location Specific Room or Area" fields)""")
          }

    def clean(self):
        cleaned_data = super(EditAsset, self).clean()

        asset_qr_location_manual = cleaned_data.get("asset_qr_location_manual")
        if asset_qr_location_manual and not QRLocation.objects.filter(pk=asset_qr_location_manual).exists():
            error = "QR Location ID does not exist!"
            self.add_error("asset_qr_location_manual", error)

        parent_assets_manual = cleaned_data.get("parent_assets_manual")
        if parent_assets_manual:
            parent_assets_manual = "".join(parent_assets_manual.split())    # remove all whitespace
            # swapping commas for whitespace allows split() to discount consecutive delimiters
            parent_assets_manual = parent_assets_manual.replace(",", " ")
            parent_assets_manual = set(parent_assets_manual.split())    # now have a deduped list
            for assetid in parent_assets_manual:
                if not Asset.objects.filter(pk=assetid).exists():
                    error = "At least One Asset ID does not exist!"
                    self.add_error("parent_assets_manual", error)


class NewAssetCalibrationInfo(forms.ModelForm):
    asset_qr_location_manual = forms.IntegerField(
                                                  required=False,
                                                  label="""AMRC QR Location ID.  (Setting this will override anything in the Asset Location
                                                   Building or Specific Location or Room)""",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )

    class Meta:
        model = Asset
        fields = [
            "asset_description", "person_responsible", "person_responsible_email", "amrc_group_responsible",
            "asset_image", "asset_details", "asset_manufacturer", "asset_model", "asset_serial_number",
            "amrc_equipment_id", "asset_status", "requires_calibration", "parent_assets", "operating_instructions",
            "handling_and_storage_instructions", "asset_location_building", "asset_location_room"
            ]
        widgets = {
            "asset_description": forms.TextInput(attrs={"class": "form-control"}),
            "asset_details": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "asset_manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "asset_model": forms.TextInput(attrs={"class": "form-control"}),
            "asset_serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "amrc_equipment_id": forms.TextInput(attrs={"class": "form-control"}),
            "asset_status": forms.Select(attrs={"class": "form-control"}),
            "person_responsible": forms.TextInput(attrs={"class": "form-control"}),
            "person_responsible_email": forms.EmailInput(attrs={"class": "form-control"}),
            "amrc_group_responsible": forms.Select(attrs={"class": "form-control"}),
            "parent_assets": forms.SelectMultiple(attrs={"class": "form-control example-enableFiltering", "style": "width: 400px;"}),
            "asset_location_building": forms.Select(attrs={"class": "form-control"}),
            "asset_location_room": forms.TextInput(attrs={"class": "form-control"}),
            "operating_instructions": forms.URLInput(attrs={"class": "form-control"}),
            "handling_and_storage_instructions": forms.URLInput(attrs={"class": "form-control"}),
        }
        labels = {
          "asset_description": ("Asset Description* "),
          "person_responsible": ("Person Responsible* "),
          "person_responsible_email": ("Person Responsible Email* "),
          "parent_assets": ("Related Assets"),
          "amrc_equipment_id": ("Engraved AMRC Metrology Equipment ID (e.g. V112 or M206B)"),
          "asset_location_room": ("Asset Location (e.g. Specific room or group etc.)"),
          "operating_instructions": ("Operating Instructions URL"),
          "handling_and_storage_instructions": ("Handling and Storage Instructions URL"),
          }

    def clean(self):
        cleaned_data = super(NewAssetCalibrationInfo, self).clean()

        asset_qr_location_manual = cleaned_data.get("asset_qr_location_manual")
        if asset_qr_location_manual and not QRLocation.objects.filter(pk=asset_qr_location_manual).exists():
            error = "QR Location ID does not exist!"
            self.add_error("asset_qr_location_manual", error)


class ReserveAssets(forms.Form):
    number_of_records_to_reserve = forms.IntegerField(
                                                      label="Number of Asset Records To Reserve* ",
                                                      widget=forms.TextInput(attrs={"class": "form-control"})
                                                      )
    asset_description = forms.CharField(
                                        label="""Asset Description Placeholder (e.g. "Reserved for IMG")* """,
                                        widget=forms.TextInput(attrs={"class": "form-control"}))
    person_responsible = forms.CharField(
                                         label="Person Responsible* ",
                                         widget=forms.TextInput(attrs={"class": "form-control"})
                                         )
    person_responsible_email = forms.EmailField(
                                                label="Person Responsible Email* ",
                                                widget=forms.EmailInput(attrs={"class": "form-control"})
                                                )
    amrc_group_responsible = forms.ModelChoiceField(
                                                    queryset=AmrcGroup.objects.all(),
                                                    label="AMRC Group Responsible* ",
                                                    widget=forms.Select(attrs={"class": "form-control"})
                                                    )


class ReserveLocations(forms.Form):
    number_of_records_to_reserve = forms.IntegerField(
                                                      label="Number of Locations Records to Reserve* ",
                                                      widget=forms.TextInput(attrs={"class": "form-control"})
                                                      )
    location_building = forms.ModelChoiceField(
                                               queryset=Buildings.objects.all(),
                                               label="Building to Reserve Locations in (can be updated later)* ",
                                               widget=forms.Select(attrs={"class": "form-control"})
                                               )
    location_room = forms.CharField(
                                    label="""Specific Location Placeholder (e.g. "Reserved for FoF Workshop"), to be updated later* """,
                                    widget=forms.TextInput(attrs={"class": "form-control"})
                                    )


class NewQRLocation(forms.ModelForm):
    class Meta:
        model = QRLocation
        fields = [
                  "building", "location_room"
                  ]
        widgets = {
                   "building": forms.Select(attrs={"class": "form-control"}),
                   "location_room": forms.TextInput(attrs={"class": "form-control"})
                   }
        labels = {
                  "building": ("Building *"),
                  "location_room": ("Specific Location (e.g. area, room or shelf etc.) *"),
                  }


class EditQRLocation(forms.ModelForm):
    class Meta:
        model = QRLocation
        fields = [
                  "building", "location_room"
                  ]
        widgets = {
                   "building": forms.Select(attrs={"class": "form-control"}),
                   "location_room": forms.TextInput(attrs={"class": "form-control"})
                   }
        labels = {
                  "building": ("Building *"),
                  "location_room": ("Specific Location (e.g. area, room or shelf etc.)"),
                  }


class EditAssetLocationInfo(forms.ModelForm):
    asset_qr_location_manual = forms.IntegerField(
                                                  required=False,
                                                  label="AMRC QR Location ID",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )

    class Meta:
        model = Asset
        fields = [
            "asset_location_building", "asset_location_room", "asset_qr_location"
            ]
        widgets = {
            "asset_location_building": forms.Select(attrs={"class": "form-control"}),
            "asset_location_room": forms.TextInput(attrs={"class": "form-control"}),
            "asset_qr_location": forms.Select(attrs={
                                                     "class": "form-control example-enableFiltering",
                                                     "style": "width: 400px;"
                                                     })
        }
        labels = {
            "asset_location_building": ("Asset Location Building"),
            "asset_location_room": ("Asset Location (e.g. Specific room or group etc.)"),
            "asset_qr_location": ("AMRC QR Location")
        }

    def clean(self):
        cleaned_data = super(EditAssetLocationInfo, self).clean()

        asset_qr_location_manual = cleaned_data.get("asset_qr_location_manual")
        if asset_qr_location_manual and not QRLocation.objects.filter(pk=asset_qr_location_manual).exists():
            error = "QR Location ID does not exist!"
            self.add_error("asset_qr_location_manual", error)


class MoveAssetToQRLocation(forms.Form):
    asset_id = forms.IntegerField(label="AMRC Asset ID To Move Here", widget=forms.TextInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned_data = super(MoveAssetToQRLocation, self).clean()

        asset_id = cleaned_data.get("asset_id")
        if not Asset.objects.filter(pk=asset_id).exists():
            error = "Asset ID Does Not Exist!"
            self.add_error("asset_id", error)


class EditAssetCalibrationInfo(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "asset_model", "asset_serial_number", "amrc_equipment_id", "asset_status",
            "person_responsible", "person_responsible_email", "amrc_group_responsible",
            "requires_calibration", "calibration_frequency", "calibration_type",
            "calibration_procedure", "asset_location_building", "asset_location_room",
            "operating_instructions", "handling_and_storage_instructions"
            ]
        widgets = {
            "asset_model": forms.TextInput(attrs={"class": "form-control"}),
            "asset_serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "amrc_equipment_id": forms.TextInput(attrs={"class": "form-control"}),
            "asset_status": forms.Select(attrs={"class": "form-control"}),
            "person_responsible": forms.TextInput(attrs={"class": "form-control"}),
            "person_responsible_email": forms.EmailInput(attrs={"class": "form-control"}),
            "amrc_group_responsible": forms.Select(attrs={"class": "form-control"}),
            "calibration_frequency": forms.TextInput(attrs={"class": "form-control"}),
            "calibration_procedure": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "asset_location_building": forms.Select(attrs={"class": "form-control"}),
            "asset_location_room": forms.TextInput(attrs={"class": "form-control"}),
            "operating_instructions": forms.URLInput(attrs={"class": "form-control"}),
            "handling_and_storage_instructions": forms.URLInput(attrs={"class": "form-control"}),
        }
        labels = {
          "amrc_equipment_id": ("Engraved AMRC Metrology Equipment ID (e.g. V112 or M206B)"),
          "asset_location_room": ("Asset Location (e.g. Specific room or group etc.)"),
          "operating_instructions": ("Operating Instructions URL"),
          "handling_and_storage_instructions": ("Handling and Storage Instructions URL"),
          }

    def clean(self):
        cleaned_data = super(EditAssetCalibrationInfo, self).clean()
        needs_calibration = cleaned_data.get("requires_calibration")
        calibration_freq = cleaned_data.get("calibration_frequency")

        if needs_calibration and not calibration_freq:
            error = "If asset requires calibration then you must enter a calibration frequency!"
            self.add_error("requires_calibration", error)
            self.add_error("calibration_frequency", error)


class EditAssetFinanceInfo(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "asset_model", "asset_serial_number", "asset_value", "requires_insurance",
            "requires_unforseen_damage_insurance",
            "charge_out_rate", "charge_code", "purchase_order_ref", "funded_by",
            "acquired_on", "disposal_date", "disposal_method",
            ]
        widgets = {
            "asset_model": forms.TextInput(attrs={"class": "form-control"}),
            "asset_serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "asset_value": forms.TextInput(attrs={"class": "form-control"}),
            "charge_out_rate": forms.TextInput(attrs={"class": "form-control"}),
            "charge_code": forms.TextInput(attrs={"class": "form-control"}),
            "purchase_order_ref": forms.TextInput(attrs={"class": "form-control"}),
            "funded_by": forms.TextInput(attrs={"class": "form-control"}),
            "acquired_on": DateInput(attrs={"class": "datepicker form-control"}),
            "disposal_date": DateInput(attrs={"class": "datepicker form-control"}),
            "disposal_method": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "asset_value": ("Asset Value £"),
            "charge_out_rate": ("Charge Out Rate £"),
        }


class Calibrate(forms.ModelForm):
    class Meta:
        model = CalibrationRecord
        fields = [
                  "asset", "calibration_description", "calibration_date", "calibration_date_next", "calibrated_by_internal",
                  "calibrated_by_external", "calibration_outcome", "calibration_notes", "calibration_certificate"
                  ]
        widgets = {
            "asset": forms.Select(attrs={"class": "form-control example-enableFiltering"}),
            "calibration_description": forms.TextInput(attrs={"class": "form-control"}),
            "calibration_date": DateInput(attrs={"class": "datepicker form-control"}),
            "calibration_date_next": DateInput(attrs={"class": "datepicker form-control"}),
            "calibrated_by_internal": forms.Select(attrs={"class": "form-control"}),
            "calibrated_by_external": forms.TextInput(attrs={"class": "form-control"}),
            "calibration_outcome": forms.Select(attrs={"class": "form-control"}),
            "calibration_notes": forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
            "calibration_certificate": forms.URLInput(attrs={"class": "form-control"}),
        }
        labels = {
                  "calibration_certificate": ("Calibration Certificate URL"),
                  }

    def clean(self):
        cleaned_data = super(Calibrate, self).clean()
        byinternal = cleaned_data.get("calibrated_by_internal")
        byexternal = cleaned_data.get("calibrated_by_external")

        if not byinternal and not byexternal:
            error = "You must enter details for either Calibrated By Internal or Calibrated By External!"
            self.add_error("calibrated_by_internal", error)
            self.add_error("calibrated_by_external", error)
        elif byinternal and byexternal:
            error = "You must select either an Internal caibrator OR an External calibrator, not both!"
            self.add_error("calibrated_by_internal", error)
            self.add_error("calibrated_by_external", error)

        calibrationdate = cleaned_data.get("calibration_date")

        if calibrationdate > timezone.now().date():
            error = "Calibration date cannot be in the future!"
            self.add_error("calibration_date", error)


FILTER_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class AssetFilter(django_filters.FilterSet):
    amrc_equipment_id = django_filters.CharFilter(
                                                  lookup_expr="exact",
                                                  label="AMRC engraved metrology equipment ID is",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )
    asset_description = django_filters.CharFilter(
                                                  lookup_expr="icontains",
                                                  label="Asset description contains",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )
    asset_status = django_filters.ModelChoiceFilter(
                                                    queryset=AssetStatus.objects.all(),
                                                    label="Asset Status",
                                                    widget=forms.Select(attrs={"class": "form-control"})
                                                    )
    asset_details = django_filters.CharFilter(
                                              lookup_expr="icontains",
                                              label="Asset details / notes contains",
                                              widget=forms.TextInput(attrs={"class": "form-control"})
                                              )
    asset_manufacturer = django_filters.CharFilter(
                                                   lookup_expr="icontains",
                                                   label="Manufacturer contains",
                                                   widget=forms.TextInput(attrs={"class": "form-control"})
                                                   )
    asset_model = django_filters.CharFilter(
                                            lookup_expr="icontains",
                                            label="Model contains",
                                            widget=forms.TextInput(attrs={"class": "form-control"})
                                            )
    asset_serial_number = django_filters.CharFilter(
                                                    lookup_expr="icontains",
                                                    label="Serial Number contains",
                                                    widget=forms.TextInput(attrs={"class": "form-control"})
                                                    )
    person_responsible = django_filters.CharFilter(
                                                   lookup_expr="icontains",
                                                   label="Person Responsible contains",
                                                   widget=forms.TextInput(attrs={"class": "form-control"})
                                                   )
    person_responsible_email = django_filters.CharFilter(
                                                         lookup_expr="icontains",
                                                         label="Person Responsible's Email contains",
                                                         widget=forms.TextInput(attrs={"class": "form-control"})
                                                         )
    amrc_group_responsible = django_filters.ModelChoiceFilter(
                                                              queryset=AmrcGroup.objects.all(),
                                                              label="AMRC Group Responsible",
                                                              widget=forms.Select(attrs={"class": "form-control"})
                                                              )
    requires_calibration = django_filters.ChoiceFilter(
                                                       choices=FILTER_CHOICES,
                                                       widget=forms.Select(attrs={"class": "form-control"})
                                                       )
    passed_calibration = django_filters.ChoiceFilter(
                                                     choices=FILTER_CHOICES,
                                                     label="Passed Last Calibration",
                                                     widget=forms.Select(attrs={"class": "form-control"})
                                                     )
    calibration_date_prev = django_filters.DateFromToRangeFilter(
                                                                widget=django_filters.widgets.RangeWidget(
                                                                                                          attrs={"class": """datepicker
                                                                                                            form-control"""}),
                                                                label="""Previous Calibration Date after first date or before second date
                                                                 or between both dates"""
                                                                )
    calibration_date_next = django_filters.DateFromToRangeFilter(
                                                                widget=django_filters.widgets.RangeWidget(attrs={"class": "datepicker form-control"}),
                                                                label="""Next Calibration Date after first date or before second date
                                                                 or between both dates"""
                                                                )
    requires_environmental_checks = django_filters.ChoiceFilter(
                                                                choices=FILTER_CHOICES,
                                                                label="Requires Environmental Checks",
                                                                widget=forms.Select(attrs={"class": "form-control"})
                                                                )
    environmental_notes = django_filters.CharFilter(
                                                    lookup_expr="icontains",
                                                    label="Environmental Notes contain",
                                                    widget=forms.TextInput(attrs={"class": "form-control"})
                                                    )
    requires_safety_checks = django_filters.ChoiceFilter(
                                                         choices=FILTER_CHOICES,
                                                         label="Requires Safety Checks",
                                                         widget=forms.Select(attrs={"class": "form-control"})
                                                         )
    safety_notes = django_filters.CharFilter(
                                             lookup_expr="icontains",
                                             label="Safety Notes contain",
                                             widget=forms.TextInput(attrs={"class": "form-control"})
                                             )
    emergency_response_information = django_filters.CharFilter(
                                                               lookup_expr="icontains",
                                                               label="Emergency Response Information contains",
                                                               widget=forms.TextInput(attrs={"class": "form-control"})
                                                               )
    requires_planned_maintenance = django_filters.ChoiceFilter(
                                                               choices=FILTER_CHOICES,
                                                               label="Requires Safety Checks",
                                                               widget=forms.Select(attrs={"class": "form-control"})
                                                               )
    maintenance_notes = django_filters.CharFilter(
                                                  lookup_expr="icontains",
                                                  label="Maintenance Notes contain",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )
    asset_value__gt = django_filters.NumberFilter(
                                                  name="asset_value",
                                                  lookup_expr="gt",
                                                  label="Asset Value greater than",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )
    asset_value__lt = django_filters.NumberFilter(
                                                  name="asset_value",
                                                  lookup_expr="lt",
                                                  label="Asset Value less than",
                                                  widget=forms.TextInput(attrs={"class": "form-control"})
                                                  )
    requires_insurance = django_filters.ChoiceFilter(
                                                     choices=FILTER_CHOICES,
                                                     label="Requires Insurance",
                                                     widget=forms.Select(attrs={"class": "form-control"})
                                                     )
    requires_unforseen_damage_insurance = django_filters.ChoiceFilter(
                                                                      choices=FILTER_CHOICES,
                                                                      label="Requires Unforseen Damage Insurance",
                                                                      widget=forms.Select(attrs={"class": "form-control"})
                                                                      )
    purchase_order_ref = django_filters.CharFilter(
                                                   lookup_expr="icontains",
                                                   label="Purchase Order Reference contains",
                                                   widget=forms.TextInput(attrs={"class": "form-control"})
                                                   )
    grn_id = django_filters.CharFilter(
                                       lookup_expr="icontains",
                                       label="AMRC Goods Receipt Note [GRN] ID contains",
                                       widget=forms.TextInput(attrs={"class": "form-control"})
                                       )
    funded_by = django_filters.CharFilter(
                                          lookup_expr="icontains",
                                          label="Funded By contains",
                                          widget=forms.TextInput(attrs={"class": "form-control"})
                                          )
    acquired_on = django_filters.DateFromToRangeFilter(
                                            widget=django_filters.widgets.RangeWidget(attrs={"class": "datepicker form-control"}),
                                            label="Date Asset Acquired after first date or before second date or between both dates"
                                            )
    disposal_date = django_filters.DateFromToRangeFilter(
                                            widget=django_filters.widgets.RangeWidget(attrs={"class": "datepicker form-control"}),
                                            label="Asset Disposal Date after first date or before second date or between both dates"
                                            )
    disposal_method = django_filters.CharFilter(
                                                lookup_expr="icontains",
                                                label="Disposal Method contains",
                                                widget=forms.TextInput(attrs={"class": "form-control"})
                                                )
    dispatch_note_id = django_filters.CharFilter(
                                                 lookup_expr="icontains",
                                                 label="AMRC Dispatch Note [DN] ID contains",
                                                 widget=forms.TextInput(attrs={"class": "form-control"})
                                                 )
    asset_qr_location = django_filters.NumberFilter(
                                              lookup_expr="exact",
                                              label="AMRC QR Location ID is",
                                              widget=forms.TextInput(attrs={"class": "form-control"})
                                              )
    asset_location_building__building_name = django_filters.CharFilter(
                                                                       lookup_expr="icontains",
                                                                       label="Location - Building Name contains",
                                                                       widget=forms.TextInput(attrs={"class": "form-control"})
                                                                       )
    asset_location_building__EFM_building_code = django_filters.CharFilter(
                                                                           lookup_expr="icontains",
                                                                           label="Location - EFM Building Code contains",
                                                                           widget=forms.TextInput(attrs={"class": "form-control"})
                                                                           )
    asset_location_room = django_filters.CharFilter(
                                                    lookup_expr="icontains",
                                                    label="Location - Specific Room or Location contains",
                                                    widget=forms.TextInput(attrs={"class": "form-control"})
                                                    )

    class Meta:
        model = Asset
        fields = ""


class QRLocationFilter(django_filters.FilterSet):
    location_id = django_filters.NumberFilter(
                                              lookup_expr="exact",
                                              label="AMRC QR Location ID is",
                                              widget=forms.TextInput(attrs={"class": "form-control"})
                                              )
    building__building_name = django_filters.CharFilter(
                                                        lookup_expr="icontains",
                                                        label="Building Name contains",
                                                        widget=forms.TextInput(attrs={"class": "form-control"})
                                                        )
    building__EFM_building_code = django_filters.CharFilter(
                                                            lookup_expr="icontains",
                                                            label="EFM Building Code contains",
                                                            widget=forms.TextInput(attrs={"class": "form-control"})
                                                            )
    location_room = django_filters.CharFilter(
                                              lookup_expr="icontains",
                                              label="Specific Room or Location contains",
                                              widget=forms.TextInput(attrs={"class": "form-control"})
                                              )

    class Meta:
        model = QRLocation
        fields = ""


class HighlightedSearchFormAssets(HighlightedSearchForm):
    def search(self):
        sqs = super(HighlightedSearchFormAssets, self).search()
        if not self.is_valid():
            return self.no_query_found()
        return sqs
