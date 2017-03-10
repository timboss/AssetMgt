from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from assetregister.models import Asset, CalibrationRecord
from assetregister.forms import EditAsset, Calibrate, AssetFilter, HighlightedSearchFormAssets, EditAssetCalibrationInfo, EditAssetFinanceInfo
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from django.http import HttpResponseNotFound
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def calibration_list(request):
    calibration_count = CalibrationRecord.objects.count()
    all_calibrations = CalibrationRecord.objects.order_by("-pk")
    paginator = Paginator(all_calibrations, 10)
    page = request.GET.get('page')
    try:
        calibrations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        calibrations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        calibrations = paginator.page(paginator.num_pages)
    return render(request, "assetregister/calibration_list.html", {
        "calibrations": calibrations, "calibration_count": calibration_count
        })


@login_required
def calibrated_asset_list(request):
    asset_count = Asset.objects.count()
    calibrated_asset_count = Asset.objects.filter(requires_calibration=True).count()
    active_calibrated_asset_count = Asset.objects.filter(requires_calibration=True,
                                                         asset_status=1).count()
    all_assets = Asset.objects.filter(requires_calibration=True).order_by("asset_status", "calibration_date_next")
    paginator = Paginator(all_assets, 10)
    page = request.GET.get('page')
    try:
        assets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        assets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        assets = paginator.page(paginator.num_pages)
    return render(request, "assetregister/calibration_asset_list.html", {
        "assets": assets, "asset_count": asset_count,
        "calibrated_asset_count": calibrated_asset_count,
        "active_calibrated_asset_count": active_calibrated_asset_count
        })


@login_required
def calibrated_asset_list_active(request):
    asset_count = Asset.objects.count()
    active_calibrated_asset_count = Asset.objects.filter(requires_calibration=True,
                                                         asset_status=1).count()
    all_assets = Asset.objects.filter(requires_calibration=True, asset_status=1).order_by("calibration_date_next")
    paginator = Paginator(all_assets, 10)
    page = request.GET.get('page')
    try:
        assets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        assets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        assets = paginator.page(paginator.num_pages)
    return render(request, "assetregister/calibration_asset_list_active.html", {
        "assets": assets, "asset_count": asset_count, "active_calibrated_asset_count": active_calibrated_asset_count
        })


def calibration_detail(request, slug):
    calibration = get_object_or_404(CalibrationRecord, slug=slug)
    return render(request, "assetregister/calibration_details.html", {"calibration": calibration})


@method_decorator(login_required, name="dispatch")
class calibration_confirm_delete(DeleteView):
    model = CalibrationRecord
    success_url = reverse_lazy("calibration_list")


@login_required
def new_calibration(request):
    if request.method == "POST":
        form = Calibrate(request.POST)
        if form.is_valid():
            calibration = form.save(commit=False)
            calibration.entered_by = request.user
            calibration.edited_on = timezone.now()
            calibration.save()
            return redirect("asset_detail", pk=calibration.asset.asset_id)
    else:
        form = Calibrate()
    return render(request, "assetregister/new_calibration.html", {"form": form})


@login_required
def calibration_edit(request, slug):
    calibration = get_object_or_404(CalibrationRecord, slug=slug)
    asset_calib_freq = calibration.asset__calibration_frequency
    if not asset_calib_freq:
        asset_calib_freq = "None Set"
    if request.method == "POST":
        form = Calibrate(request.POST, instance=calibration)
        if form.is_valid():
            calibration = form.save(commit=False)
            calibration.calibration_entered_by = request.user
            calibration.calibration_entered_on = timezone.now()
            calibration.save()
            return redirect("asset_detail", pk=calibration.asset.asset_id)
    else:
        form = Calibrate(instance=calibration)
    return render(request, "assetregister/new_calibration.html", {"form": form,
                                                                  "asset_calib_freq": asset_calib_freq})


@login_required
def new_calibration_asset(request, urlpk):
    asset_calib_freq = Asset.objects.values_list("calibration_frequency", flat=True).get(asset_id=urlpk)
    if not asset_calib_freq:
        asset_calib_freq = "None Set"
    disable_asset = True
    if request.method == "POST":
        form = Calibrate(request.POST)
        if form.is_valid():
            calibration = form.save(commit=False)
            calibration.calibration_entered_by = request.user
            calibration.calibration_entered_on = timezone.now()
            calibration.save()
            return redirect("asset_detail", pk=calibration.asset.asset_id)
    else:
        form = Calibrate(initial={"asset": urlpk})
    return render(request, "assetregister/new_calibration.html", {"form": form,
                                                                  "asset_calib_freq": asset_calib_freq})
