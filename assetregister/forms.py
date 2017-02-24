from django import forms
from .models import Asset, CalibrationRecord
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

class DateInput(forms.DateInput):
    input_type = 'date'

class EditAsset(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "asset_description", "asset_image", "asset_details", "asset_manufacturer", "asset_model",
            "asset_serial_number", "asset_status", "person_responsible", "person_responsible_email",
            "requires_calibration", "calibration_instructions", "requires_insurance", 
            "requires_safety_checks", "requires_environmental_checks", "requires_planned_maintenance", 
            "maintenance_instructions", "maintenance_records", "asset_value",
            "purchase_order_ref", "funded_by", "acquired_on", "parent_assets", "asset_location_building",
            "asset_location_room", "asset_operating_instructions", "asset_handling_and_storage_instructions"
            ]
        widgets = {
            'acquired_on': DateInput(attrs={'class': 'datepicker'}),
        }
        


class Calibrate(forms.ModelForm):
    class Meta:
        model = CalibrationRecord
        fields = [
                  "asset", "calibration_description", "calibration_date", "calibration_date_next", "calibrated_by_internal",
                  "calibrated_by_external", "calibration_outcome", "calibration_notes", "calibration_certificate"
                  ]
        widgets = {
            'calibration_date': DateInput(attrs={'class': 'datepicker'}),
            'calibration_date_next': DateInput(attrs={'class': 'datepicker'}),
        }
        labels = {
                  "calibration_certificate": ("Calibration Certificate URL"),
                  }


class CalibrationSearch(SearchForm):
    calibration_due_before = forms.DateField(required=False)
    calibration_due_after = forms.DateField(required=False)

    def search(self):
        # First we need to store SearchQuerySet recieved after / from any other processing that's going on
        # sqs = super(CalibrationSearch, self).search() <- This looks for a field called 'content'

        sqs = SearchQuerySet().all()
        # searchqueryset = sqs

        if not self.is_valid():
            # return self.no_query_found()
            return self.SearchQuerySet().all()

        if self.is_valid():
            # check to see if any date filters used, if so apply filter
            if self.cleaned_data['calibration_due_before']:
                sqs = sqs.filter(calibration_date_next__lte=self.cleaned_data['calibration_due_before'])

            if self.cleaned_data['calibration_due_after']:
                sqs = sqs.filter(calibration_date_next__gte=self.cleaned_data['calibration_due_after'])

            return sqs
