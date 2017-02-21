from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import Asset
from .forms import EditAsset, CalibrationSearch, Calibrate
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from djqscsv import render_to_csv_response
from django.http import HttpResponseNotFound


def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status="Active / In-Use").count()
    assets = Asset.objects.order_by("asset_id")
    return render(request, "assetregister/asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        })


def active_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status="Active / In-Use").count()
    assets = Asset.objects.filter(asset_status="Active / In-Use").order_by("asset_id")
    return render(request, "assetregister/asset_list_active.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        })


def calibrated_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status="Active / In-Use").count()
    calibrated_asset_count = Asset.objects.filter(requires_calibration=True).count()
    active_calibrated_asset_count = Asset.objects.filter(requires_calibration=True,
                                                         asset_status="Active / In-Use").count()
    assets = Asset.objects.filter(requires_calibration=True).order_by("asset_status", "calibration_date_next")
    return render(request, "assetregister/calibration_asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count,
        "calibrated_asset_count": calibrated_asset_count,
        "active_calibrated_asset_count": active_calibrated_asset_count
        })


def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    # ToDo - "ParentOf" field
    #     - Status number -> words translation
    return render(request, "assetregister/asset_details.html", {"asset": asset})


def asset_qr(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, "assetregister/asset_qr.html", {"asset": asset})


def asset_qr_small(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, "assetregister/asset_qr_small.html", {"asset": asset})


@login_required
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


@login_required
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
            i
    else:
        form = EditAsset(instance=asset)
    return render(request, "assetregister/asset_edit.html", {"form": form})


# Depreciated this "quick delete" in favour of using Django's _
# built in generic DeleteView class view to require manually confirming deletion

# @login_required
# def asset_remove(request, pk):
#    asset = get_object_or_404(Asset, pk=pk)
#    asset.delete()
#    return redirect("asset_list")


@method_decorator(login_required, name="dispatch")
class asset_confirm_delete(DeleteView):
    model = Asset
    success_url = reverse_lazy("asset_list")


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


def calibrated_asset_export_active(request):
    calibration_export = Asset.objects.filter(requires_calibration=True,
                                              asset_status="Active / In-Use").order_by("calibration_date_next").values(
                                                "asset_id", "requires_calibration", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "calibration_date_prev", "calibration_date_next",
                                                "calibration_instructions", "person_responsible",
                                                "person_responsible_email", "asset_location_building",
                                                "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Active_Assets_Needing_Calibration.csv")


def calibrated_asset_export_all(request):
    calibration_export = Asset.objects.filter(requires_calibration=True).order_by("calibration_date_next").values(
                                                "asset_id", "requires_calibration", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status", "calibration_date_prev", "calibration_date_next",
                                                "calibration_instructions", "person_responsible",
                                                "person_responsible_email", "asset_location_building",
                                                "asset_location_room")
    return render_to_csv_response(calibration_export, filename="All_Assets_Needing_Calibration.csv")


def calibration_asset_export_nextmonth(request):
    plusonemonth = timezone.now() + timedelta(days=30)
    calibration_export = Asset.objects.filter(requires_calibration=True,
                                              calibration_date_next__lte=plusonemonth).order_by("calibration_date_next").values("asset_id", "requires_calibration", "asset_description", "asset_manufacturer", "asset_model", "asset_serial_number", "asset_status", "calibration_date_prev", "calibration_date_next", "calibration_instructions", "person_responsible", "person_responsible_email", "asset_location_building", "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Assets_Due_Calibration_Before_" +
                                  str(plusonemonth.date()) + ".csv")


def calibration_asset_export_custom_select(request):
    return render(request, "assetregister/calibration_export.html")


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
