from django import forms
from .models import Asset, CalibrationRecord
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from django.utils import timezone
import django_filters


class DateInput(forms.DateInput):
    input_type = 'date'


class EditAsset(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "asset_description", "asset_image", "asset_details", "asset_manufacturer", "asset_model",
            "asset_serial_number", "amrc_equipment_id", "asset_status", "person_responsible", "person_responsible_email",
            "requires_calibration", "calibration_instructions", "requires_safety_checks",
            "requires_environmental_checks", "environmental_aspects", "environmental_notes",
            "requires_planned_maintenance", "maintenance_instructions", "maintenance_records",
            "asset_value", "requires_insurance", "purchase_order_ref", "funded_by", "acquired_on", "disposal_date",
            "parent_assets", "asset_location_building", "asset_location_room", "operating_instructions",
            "handling_and_storage_instructions"
            ]
        widgets = {
            'asset_description': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_details': forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),
            'asset_manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_model': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amrc_equipment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_status': forms.Select(attrs={'class': 'form-control'}),
            'person_responsible': forms.TextInput(attrs={'class': 'form-control'}),
            'person_responsible_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'calibration_instructions': forms.URLInput(attrs={'class': 'form-control'}),
            'environmental_aspects': forms.CheckboxSelectMultiple(),
            'environmental_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),
            'maintenance_instructions': forms.URLInput(attrs={'class': 'form-control'}),
            'maintenance_records': forms.URLInput(attrs={'class': 'form-control'}),
            'asset_value': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_ref': forms.TextInput(attrs={'class': 'form-control'}),
            'funded_by': forms.TextInput(attrs={'class': 'form-control'}),
            'acquired_on': DateInput(attrs={'class': 'datepicker form-control'}),
            'disposal_date': DateInput(attrs={'class': 'datepicker form-control'}),
            'parent_assets': forms.SelectMultiple(attrs={'class': 'form-control example-enableFiltering', 'style': 'width: 400px;'}),
            'asset_location_building': forms.Select(attrs={'class': 'form-control'}),
            'asset_location_room': forms.TextInput(attrs={'class': 'form-control'}),
            'operating_instructions': forms.URLInput(attrs={'class': 'form-control'}),
            'handling_and_storage_instructions': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
          "parent_assets": ("Related Assets"),
          "amrc_equipment_id": ("AMRC Equipment ID (e.g. V112, B05 or M206B"),
          "asset_location_room": ("Asset Location (e.g. Specific room or group etc.)")
          }


class Calibrate(forms.ModelForm):
    class Meta:
        model = CalibrationRecord
        fields = [
                  "asset", "calibration_description", "calibration_date", "calibration_date_next", "calibrated_by_internal",
                  "calibrated_by_external", "calibration_outcome", "calibration_notes", "calibration_certificate"
                  ]
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-control example-enableFiltering'}),
            'calibration_description': forms.TextInput(attrs={'class': 'form-control'}),
            'calibration_date': DateInput(attrs={'class': 'datepicker form-control'}),
            'calibration_date_next': DateInput(attrs={'class': 'datepicker form-control'}),
            'calibrated_by_internal': forms.Select(attrs={'class': 'form-control'}),
            'calibrated_by_external': forms.TextInput(attrs={'class': 'form-control'}),
            'calibration_outcome': forms.Select(attrs={'class': 'form-control'}),
            'calibration_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),
            'calibration_certificate': forms.URLInput(attrs={'class': 'form-control'}),
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


class AssetFilter(django_filters.FilterSet):
    asset_id = django_filters.NumberFilter(lookup_expr="exact")
    asset_description = django_filters.CharFilter(lookup_expr="icontains")
    asset_details = django_filters.CharFilter(lookup_expr="icontains")
    asset_manufacturer = django_filters.CharFilter(lookup_expr="icontains")
    asset_model = django_filters.CharFilter(lookup_expr="icontains")
    asset_serial_number = django_filters.CharFilter(lookup_expr="icontains")
    amrc_equipment_id = django_filters.CharFilter(lookup_expr="icontains")
    person_responsible = django_filters.CharFilter(lookup_expr="icontains")
    person_responsible_email = django_filters.CharFilter(lookup_expr="icontains")
    environmental_notes = django_filters.CharFilter(lookup_expr="icontains")
    asset_value__gt = django_filters.NumberFilter(name="asset_value", lookup_expr="gt")
    asset_value__lt = django_filters.NumberFilter(name="asset_value", lookup_expr="lt")
    purchase_order_ref = django_filters.CharFilter(lookup_expr="exact")
    funded_by = django_filters.CharFilter(lookup_expr="icontains")
    acquired_on__gt = django_filters.DateFilter(name="acquired_on", lookup_expr="acquired_on__gt")
    acquired_on__lt = django_filters.DateFilter(name="acquired_on", lookup_expr="acquired_on__lt")
    disposal_date__gt = django_filters.DateFilter(name="disposal_date", lookup_expr="disposal_date__gt")
    disposal_date__lt = django_filters.DateFilter(name="disposal_date", lookup_expr="disposal_date__lt")
    
    asset_location_building__building_name = django_filters.CharFilter(lookup_expr="icontains")
    asset_location_building__EFM_building_code = django_filters.CharFilter(lookup_expr="icontains")
    asset_location_room = django_filters.CharFilter(lookup_expr="icontains")
    
    class Meta:
        model = Asset
        fields = ["requires_calibration", "requires_safety_checks", "requires_environmental_checks",
                  "requires_planned_maintenance", "requires_insurance"]
        labels = {
          "amrc_equipment_id": ("AMRC Equipment ID (no spaces) e.g. V112, B05 or M206B"),
          "asset_location_room": ("Asset Location (specific room or group etc.)")
          }
