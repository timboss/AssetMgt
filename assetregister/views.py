from django.shortcuts import render
from .models import Asset

# Create your views here.

def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    assets = Asset.objects.filter(asset_status=1).order_by("asset_id")
    return render(request, "assetregister/asset_list.html", {"assets": assets}) 