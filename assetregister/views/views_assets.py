from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from assetregister.models import Asset, CalibrationRecord, CalibrationAssetNotificaton, HighValueAssetNotification, EnvironmentalAspectAssetNoficiation
from assetregister.forms import EditAsset, Calibrate, AssetFilter, HighlightedSearchFormAssets, EditAssetCalibrationInfo, EditAssetFinanceInfo
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from django.http import HttpResponseNotFound
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)


def examplemodal(request):
    return render(request, "assetregister/example2.html")


def home(request):
    baseurl = settings.BASEURL
    return render(request, "assetregister/home.html", {"baseurl": baseurl})


def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    all_assets = Asset.objects.order_by("asset_id")
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
    return render(request, "assetregister/asset_list.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count,
        })


def asset_list_filter(request):
    if request.GET:
        filter = AssetFilter(request.GET, queryset=Asset.objects.all())
        #paginator = Paginator(filter_all, 10)
        #page = request.GET.get('page')
        #try:
        #    filter = paginator.page(page)
        #except PageNotAnInteger:
        #    # If page is not an integer, deliver first page.
        #    filter = paginator.page(1)
        #except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
        #    filter = paginator.page(paginator.num_pages)
    else:
        #this is a bit hacky, but should work forever...
        filter = AssetFilter(request.GET, queryset=Asset.objects.filter(asset_status=9999))
    return render(request, "assetregister/asset_list_filtered.html", {"filter": filter, 
        })


def active_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    all_assets = Asset.objects.filter(asset_status=1).order_by("asset_id")
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
    return render(request, "assetregister/asset_list_active.html", {
        "assets": assets, "asset_count": asset_count, "active_asset_count": active_asset_count
        })


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


def asset_detail_equipid(request, equipid):
    asset = get_object_or_404(Asset, amrc_equipment_id=equipid)
    pk = asset.asset_id
    return asset_detail(request, pk)


def asset_qr(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/asset_qr.html", {"asset": asset, "baseurl":baseurl})


def asset_qr_small(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/asset_qr_small.html", {"asset": asset, "baseurl":baseurl})


CalEmails = CalibrationAssetNotificaton.objects.all().values_list("email_address", flat=True)
EnviroEmails = EnvironmentalAspectAssetNoficiation.objects.all().values_list("email_address", flat=True)

def calibrated_asset_email(pk):
    logger.info('composing calibrate email')
    asset = Asset.objects.get(pk=pk)
    email_subject = "[AMRC AssetMgt] Asset Requires Calibration"
    mail_body = """An asset on the AMRC Asset Management System has just been set to "Requires Calibration".
                 <br /><br /> "Asset No. {}" <br /><br />
                 <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System
                 """.format(asset, settings.BASEURL, asset.asset_id)
    print("""sending "{}" to {}""".format(mail_body, CalEmails))
    send_mail(email_subject, "", settings.EMAIL_FROM, CalEmails, fail_silently=False, html_message=mail_body)


def high_value_asset_email(assetpk, value):
    asset = Asset.objects.get(pk=assetpk)
    allnotifications = HighValueAssetNotification.objects.all()
    email_subject = "[AMRC AssetMgt] High Value Asset"
    for notification in allnotifications:
        email_on_value = notification.if_asset_value_above
        if value >= email_on_value:
            email_to = HighValueAssetNotification.objects.filter(pk=notification.pk).values_list("email_address", flat=True)
            print(email_to)
            mail_body = """An asset on the AMRC Asset Management System has just had it's value set to be greater than your trigger value of {}.
                     <br /><br /> "Asset No. {}" <br />
                     Asset Value = £{} <br /><br />
                     <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System
                     """.format(email_on_value, asset, value, settings.BASEURL, assetpk)
            print("""sending "{}" to {}""".format(mail_body, email_to))
            send_mail(email_subject, "", settings.EMAIL_FROM, email_to, fail_silently=False, html_message=mail_body)


def enviro_aspect_asset_email(pk):
    asset = Asset.objects.get(pk=pk)
    email_subject = "[AMRC AssetMgt] Asset With Environmental Aspects"
    mail_body = """An asset on the AMRC Asset Management System has just been associated with Envrionmental Aspects.<br /><br />
                 "Asset No. {}" <br /><br />
                 <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System
                 """.format(asset, asset.environmental_notes, settings.BASEURL, asset.asset_id)
    print("""sending "{}" to {}""".format(mail_body, EnviroEmails))
    send_mail(email_subject, "", settings.EMAIL_FROM, EnviroEmails, fail_silently=False, html_message=mail_body)


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
            if asset.requires_calibration:
                calibrated_asset_email(asset.asset_id)
            if asset.environmental_aspects:
                enviro_aspect_asset_email(asset.asset_id)
            if asset.asset_value:
                high_value_asset_email(asset.asset_id, asset.asset_value)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset()
    return render(request, "assetregister/asset_edit.html", {"form": form})


@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    assets_to_relate = Asset.objects.exclude(pk=pk).order_by("asset_manufacturer", "asset_description")
    cur_calibration_status = asset.requires_calibration
    cur_enviro_aspects = asset.environmental_aspects
    cur_value = asset.asset_value
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            form.save_m2m()
            if cur_calibration_status != asset.requires_calibration and asset.requires_calibration:
                # Calibration status has just changed and is now true
                calibrated_asset_email(asset.asset_id)
            print(cur_enviro_aspects)
            print(asset.environmental_aspects)
            
            #FIX THIS - ENVIRO ASPECTS ALWAYS = NONE!
            
            
            if cur_enviro_aspects != asset.environmental_aspects and asset.environmental_aspects:
                # Enviro aspects have changed and asset has enviro aspects
                enviro_aspect_asset_email(asset.asset_id)
            if cur_value != asset.asset_value:
                # Value has changed and value >= £5k
                high_value_asset_email(asset.asset_id, asset.asset_value)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset(instance=asset)
    return render(request, "assetregister/asset_edit.html", {"form": form, "assets_to_relate": assets_to_relate})


@login_required
def edit_asset_calibration_info(request, pk):
    type = "Calibration"
    asset = get_object_or_404(Asset, pk=pk)
    asset_id = asset.asset_id
    asset_description = asset.asset_description
    asset_manufacturer = asset.asset_manufacturer
    cur_calibration_status = asset.requires_calibration
    if request.method == "POST":
        form = EditAssetCalibrationInfo(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            if cur_calibration_status != asset.requires_calibration and asset.requires_calibration:
                # Calibration status has just changed and is now true
                calibrated_asset_email(asset.asset_id)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAssetCalibrationInfo(instance=asset)
    return render(request, "assetregister/asset_edit_disabledfields.html", {"form": form, "type": type,
                                                            "asset_id": asset_id, "manufacturer": asset_manufacturer,
                                                            "description": asset_description})


@login_required
def edit_asset_finance_info(request, pk):
    type = "Finance"
    asset = get_object_or_404(Asset, pk=pk)
    asset_id = asset.asset_id
    asset_description = asset.asset_description
    asset_manufacturer = asset.asset_manufacturer
    cur_value = asset.asset_value
    if request.method == "POST":
        form = EditAssetFinanceInfo(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.save()
            if cur_value != asset.asset_value and asset.asset_value > 4999.99:
                # Valu has changed and value >= £5k
                high_value_asset_email(asset.asset_id)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAssetFinanceInfo(instance=asset)
    return render(request, "assetregister/asset_edit_disabledfields.html", {"form": form, "type": type,
                                                             "asset_id": asset_id, "manufacturer": asset_manufacturer,
                                                             "description": asset_description})


@method_decorator(login_required, name="dispatch")
class asset_confirm_delete(DeleteView):
    model = Asset
    success_url = reverse_lazy("asset_list")


class NewSearchView(SearchView):
    template_name = 'search/search.html'
    queryset = SearchQuerySet().exclude(asset_id=999999999999999999999999)
    form_class = HighlightedSearchFormAssets
