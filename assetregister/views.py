from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Asset
from .forms import EditAsset

# Create your views here.

def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    assets = Asset.objects.order_by("asset_id")
    return render(request, "assetregister/asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        }) 

def active_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    assets = Asset.objects.filter(asset_status=1).order_by("asset_id")
    return render(request, "assetregister/asset_list_active.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        }) 

def calibrated_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    calibrated_asset_count = Asset.objects.filter(requires_calibration=True).count()
    active_calibrated_asset_count = Asset.objects.filter(requires_calibration=True, asset_status=1).count()
    assets = Asset.objects.filter(requires_calibration=True).order_by("-calibration_date_next")
    return render(request, "assetregister/calibrated_asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count, "calibrated_asset_count": calibrated_asset_count, "active_calibrated_asset_count": active_calibrated_asset_count
        })
    
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    #ToDo - "ParentOf" field
    #     - Status number -> words translation
    return render(request, "assetregister/asset_details.html", {"asset": asset})

def asset_new(request):
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset()
    return render(request, "assetregister/asset_edit.html", {"form": form})

def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset(instance=asset)
    return render(request, "assetregister/asset_edit.html", {"form": form})