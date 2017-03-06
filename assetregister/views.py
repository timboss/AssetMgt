from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import Asset, CalibrationRecord
from .forms import EditAsset, CalibrationSearch, Calibrate, AssetFilter
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from djqscsv import render_to_csv_response
from django.http import HttpResponseNotFound
from django.conf import settings


def examplemodal(request):
    return render(request, "assetregister/example.html")


def home(request):
    baseurl = settings.BASEURL
    return render(request, "assetregister/home.html", {"baseurl": baseurl})


def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    assets = Asset.objects.order_by("asset_id")
    return render(request, "assetregister/asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count,
        })

def asset_list_filter(request):
    if request.GET:
        filter = AssetFilter(request.GET, queryset=Asset.objects.all())
    else:
        #this is a bit hacky, but should work forever...
        filter = AssetFilter(request.GET, queryset=Asset.objects.filter(asset_status=9999))
    return render(request, "assetregister/asset_list_filtered.html", {"filter": filter, 
        })

def active_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    assets = Asset.objects.filter(asset_status=1).order_by("asset_id")
    return render(request, "assetregister/asset_list_active.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        })


@login_required
def calibration_list(request):
    calibration_count = CalibrationRecord.objects.count()
    calibrations = CalibrationRecord.objects.order_by("-pk")
    return render(request, "assetregister/calibration_list.html", {
        "calibrations": calibrations, "calibration_count": calibration_count
        })


@login_required
def calibrated_asset_list(request):
    asset_count = Asset.objects.count()
    calibrated_asset_count = Asset.objects.filter(requires_calibration=True).count()
    active_calibrated_asset_count = Asset.objects.filter(requires_calibration=True,
                                                         asset_status=1).count()
    assets = Asset.objects.filter(requires_calibration=True).order_by("asset_status", "calibration_date_next")
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
    assets = Asset.objects.filter(requires_calibration=True, asset_status=1).order_by("calibration_date_next")
    return render(request, "assetregister/calibration_asset_list_active.html", {
        "assets": assets, "asset_count": asset_count, "active_calibrated_asset_count": active_calibrated_asset_count
        })


def calibration_detail(request, slug):
    calibration = get_object_or_404(CalibrationRecord, slug=slug)
    return render(request, "assetregister/calibration_details.html", {"calibration": calibration})


def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    assetcalibrations_3 = CalibrationRecord.objects.filter(asset=pk).order_by("-calibration_date", "-calibration_record_id")[:3]
    assetcalibrations_all = CalibrationRecord.objects.filter(asset=pk).order_by("-calibration_date", "-calibration_record_id")
    parent_of = Asset.objects.filter(parent_assets=pk)
    enviro_aspect_count = Asset.objects
    curdate = timezone.now().date()
    if assetcalibrations_3.count() > 0:
        last_cal = CalibrationRecord.objects.filter(asset=pk).order_by("-calibration_date", "-calibration_record_id")[0]
        if last_cal.calibration_date_next and last_cal.calibration_outcome == "Pass" and last_cal.calibration_date_next >= timezone.now().date():
            calibration_OK = True
        else:
            calibration_OK = False
        return render(request, "assetregister/asset_details.html", {"asset": asset, "calibrations": assetcalibrations_3,
                                                                    "parent_of": parent_of, "last_cal": last_cal,
                                                                    "allcalibrations": assetcalibrations_all,
                                                                    "calibration_OK": calibration_OK, "curdate": curdate})
    else:
        return render(request, "assetregister/asset_details.html", {"asset": asset, "calibrations": assetcalibrations_3,
                                                                    "parent_of": parent_of, "curdate": curdate})


def asset_qr(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/asset_qr.html", {"asset": asset, "baseurl":baseurl})


def asset_qr_small(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/asset_qr_small.html", {"asset": asset, "baseurl":baseurl})


@login_required
def asset_new(request):
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            form.save_m2m()
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset()
    return render(request, "assetregister/asset_edit.html", {"form": form})


@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    assets_to_relate = Asset.objects.exclude(asset_id=pk).order_by("asset_manufacturer", "asset_description")
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            form.save_m2m()
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset(instance=asset)
    return render(request, "assetregister/asset_edit.html", {"form": form, "assets_to_relate": assets_to_relate})


@method_decorator(login_required, name="dispatch")
class asset_confirm_delete(DeleteView):
    model = Asset
    success_url = reverse_lazy("asset_list")


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
    if request.method == "POST":
        form = Calibrate(request.POST, instance=calibration)
        if form.is_valid():
            calibration = form.save(commit=False)
            calibration.entered_by = request.user
            calibration.edited_on = timezone.now()
            calibration.save()
            return redirect("asset_detail", pk=calibration.asset.asset_id)
    else:
        form = Calibrate(instance=calibration)
    return render(request, "assetregister/new_calibration.html", {"form": form})


@login_required
def new_calibration_asset(request, urlpk):
    if request.method == "POST":
        form = Calibrate(request.POST)
        if form.is_valid():
            calibration = form.save(commit=False)
            calibration.entered_by = request.user
            calibration.edited_on = timezone.now()
            calibration.save()
            return redirect("asset_detail", pk=calibration.asset.asset_id)
    else:
        form = Calibrate(initial={"asset": urlpk})
    return render(request, "assetregister/new_calibration.html", {"form": form})


class calibration_search(SearchView):
    template_name = 'search/search.html'
    form_class = CalibrationSearch
    queryset = SearchQuerySet().filter(requires_calibration=True)
#    return render(request, template, {'form' : form_class})

#    def get_queryset(self):
#        queryset = super(calibration_search, self).get_queryset()
#        return queryset


@login_required
def calibrated_asset_export_active(request):
    calibration_export = Asset.objects.filter(requires_calibration=True,
                                              asset_status="Active / In-Use").order_by("calibration_date_next").values(
                                                "asset_id", "requires_calibration", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "calibration_date_prev", "calibration_date_next",
                                                "calibration_instructions", "person_responsible",
                                                "person_responsible_email", "asset_location_building",
                                                "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Active_Assets_Needing_Calibration_" + str(timezone.now().date()) + ".csv")


@login_required
def calibrated_asset_export_all(request):
    calibration_export = Asset.objects.filter(requires_calibration=True).order_by("calibration_date_next").values(
                                                "asset_id", "requires_calibration", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "calibration_date_prev", "calibration_date_next",
                                                "calibration_instructions", "person_responsible",
                                                "person_responsible_email", "asset_location_building",
                                                "asset_location_room")
    return render_to_csv_response(calibration_export, filename="All_Assets_Needing_Calibration_" + str(timezone.now().date()) + ".csv")


@login_required
def calibration_asset_export_nextmonth(request):
    plusonemonth = timezone.now() + timedelta(days=30)
    calibration_export = Asset.objects.filter(requires_calibration=True,
                                              calibration_date_next__lte=plusonemonth).order_by("calibration_date_next").values("asset_id", "requires_calibration", "asset_description", "asset_manufacturer", "asset_model", "asset_serial_number", "asset_status", "calibration_date_prev", "calibration_date_next", "calibration_instructions", "person_responsible", "person_responsible_email", "asset_location_building", "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Assets_Due_Calibration_Before_" +
                                  str(plusonemonth.date()) + ".csv")


@login_required
def calibration_asset_export_custom_select(request):
    return render(request, "assetregister/calibration_export.html")


@login_required
def calibration_asset_export_custom(request):
    if request.GET.get('days'):
        getdays = int(request.GET.get('days'))
        newdate = timezone.now() + timedelta(days=getdays)
        newdate = newdate.date()
    elif request.GET.get('date'):
        newdate = request.GET.get('date')
    else:
        return HttpResponseNotFound('<h2>No "?day=" or "?date=" URL GET parameters found!</h2>')
    calibration_export = Asset.objects.filter(requires_calibration=True, calibration_date_next__lte=newdate).order_by("calibration_date_next").values("asset_id", "requires_calibration", "asset_description", "asset_manufacturer", "asset_model", "asset_serial_number", "asset_status", "calibration_date_prev", "calibration_date_next", "calibration_instructions", "person_responsible", "person_responsible_email", "asset_location_building", "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Assets_Due_Calibration_Before_" + str(newdate) + ".csv")


def maintenance_export_all(request):
    export = Asset.objects.filter(requires_planned_maintenance=True).order_by("asset_id").values(
                                                "asset_id", "requires_planned_maintenance", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "person_responsible", "person_responsible_email",
                                                "maintenance_instructions", "maintenance_records",
                                                "parent_assets", "asset_location_building", "asset_location_room",
                                                "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Maintenance_" + str(timezone.now().date()) + ".csv")


def environmental_export_all(request):
    export = Asset.objects.filter(requires_environmental_checks=True).order_by("asset_id").values(
                                                "asset_id", "requires_environmental_checks", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "person_responsible", "person_responsible_email",
                                                "parent_assets", "asset_location_building", "asset_location_room",
                                                "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Environmental_Checks_" + str(timezone.now().date()) + ".csv")


def insurance_export_all(request):
    export = Asset.objects.filter(requires_insurance=True).order_by("asset_id").values(
                                                "asset_id", "requires_insurance", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "asset_value", "purchase_order_ref",
                                                "funded_by", "acquired_on", "person_responsible", "person_responsible_email",
                                                "parent_assets", "asset_location_building",
                                                "asset_location_room", "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Insurance_" + str(timezone.now().date()) + ".csv")


def safety_export_all(request):
    export = Asset.objects.filter(requires_safety_checks=True).order_by("asset_id").values(
                                                "asset_id", "requires_safety_checks", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "person_responsible", "person_responsible_email",
                                                "parent_assets", "asset_location_building", "asset_location_room",
                                                "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Safety_Checks_" + str(timezone.now().date()) + ".csv")


@login_required
def export_all_assets(request):
    export = Asset.objects.all()
    return render_to_csv_response(export, filename="All_Assets__" + str(timezone.now().date()) + ".csv")
