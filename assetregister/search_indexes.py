from haystack import indexes
from .models import Asset


class AssetIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)
    #'text' "doc & template = true" uses asset_text.txt data template
    #asset_description = indexes.CharField(model_attr='asset_description')
    manufacturer = indexes.CharField(model_attr='asset_manufacturer')
    model = indexes.CharField(model_attr='asset_model')
    #serial_no = indexes.CharField(model_attr='asset_serial_number')
    person_responsible = indexes.CharField(model_attr='person_responsible')
    #person_responsible_email = indexes.CharField(model_attr='person_responsible_email')
    #purchase_order_ref = indexes.CharField(model_attr='purchase_order_ref')
    #funded_by = indexes.CharField(model_attr='funded_by')
    asset_location_building = indexes.CharField(model_attr='asset_location_building')
    #asset_location_room = indexes.CharField(model_attr='asset_location_room')
    # ^ All the above is now stored as one field "text", see asset_text.txt data template doc

    def get_model(self):
        return Asset

    def no_query_found(self):
        return self.searchqueryset.exclude(content='foo')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects