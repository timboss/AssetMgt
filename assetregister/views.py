from django.shortcuts import render, get_object_or_404
from .models import Asset

# Create your views here.

def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    assets = Asset.objects.filter(asset_status=1).order_by("asset_id")
    return render(request, "assetregister/asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        }) 
    
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    #ToDo - "ParentOf" field
    #     - Status number -> words translation
    return render(request, "assetregister/asset_details.html", {"asset": asset})