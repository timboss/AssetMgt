from django import forms
from .models import Asset
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet


class EditAsset(forms.ModelForm):  
    class Meta:
        model = Asset
        fields =  [
            "asset_description", "asset_image", "asset_details", "asset_manufacturer", "asset_model", "asset_serial_number", "asset_status",
            "person_responsible", "person_responsible_email", "requires_calibration", "calibration_instructions", "calibration_date_prev", 
            "calibration_date_next", "requires_insurance", "requires_safety_checks", "requires_environmental_checks", "requires_planned_maintenance", 
            "maintenance_instructions", "asset_value", "purchase_order_ref", "funded_by", "acquired_on", "related_to_other_asset", 
            "asset_location_building", "asset_location_room",
            ]
        
class CalibrationSearch(SearchForm):
    calibration_due_before = forms.DateField(required=False)
    calibration_due_after = forms.DateField(required=False)
    
    def search(self):
        #First we need to store SearchQuerySet recieved after / from any other processing that's going on
        #sqs = super(CalibrationSearch, self).search() <- This looks for a field called 'content'
        
        sqs = SearchQuerySet().all()
        searchqueryset = sqs
        
        if not self.is_valid():
        #    return self.no_query_found()
            return self.SearchQuerySet().all()
        
        if self.is_valid():
            #check to see if any date filters used, if so apply filter
            if self.cleaned_data['calibration_due_before']:
                sqs = sqs.filter(calibration_date_next__lte=self.cleaned_data['calibration_due_before'])
            
            if self.cleaned_data['calibration_due_after']:
                sqs = sqs.filter(calibration_date_next__gte=self.cleaned_data['calibration_due_after'])
        
            return sqs