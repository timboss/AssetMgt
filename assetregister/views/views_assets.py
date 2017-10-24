from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from assetregister.models import (Asset,
                                  CalibrationRecord,
                                  CalibrationAssetNotificaton,
                                  HighValueAssetNotification,
                                  EnvironmentalAspectAssetNoficiation,
                                  ArchivedAssetNotificaton,
                                  QRLocation
                                  )
from assetregister.forms import (EditAsset,
                                 AssetFilter,
                                 # HighlightedSearchFormAssets,
                                 EditAssetCalibrationInfo,
                                 EditAssetFinanceInfo,
                                 ReserveAssets,
                                 NewAssetCalibrationInfo,
                                 )
from assetregister.decorators import group_required
# from haystack.generic_views import SearchView
# from haystack.query import SearchQuerySet
import logging
from background_task import background
from haystack.management.commands import update_index
from djqscsv import render_to_csv_response


# Get an instance of a logger
logger = logging.getLogger(__name__)


@background()
def reindex_whoosh():
    update_index.Command().handle(interactive=False, remove=True, age=1)
    # age=1 will only add assets edited in last hour.


@login_required
def home(request):
    baseurl = settings.BASEURL
    return render(request, "assetregister/home.html", {"baseurl": baseurl})


@login_required
def asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    all_assets = Asset.objects.order_by("asset_id")
    paginator = Paginator(all_assets, 10)
    page = request.GET.get("page")
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


@login_required
def active_asset_list(request):
    asset_count = Asset.objects.count()
    active_asset_count = Asset.objects.filter(asset_status=1).count()
    all_assets = Asset.objects.filter(asset_status=1).order_by("asset_id")
    paginator = Paginator(all_assets, 10)
    page = request.GET.get("page")
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


@login_required
def asset_list_filter(request):
    if request.GET:
        filter = AssetFilter(request.GET, queryset=Asset.objects.all())
        makecsv = request.GET.get("makecsv")
        if makecsv == "1":
            # User selected CSV output on form
            output = filter.qs.values("asset_id", "amrc_equipment_id", "asset_status__status_name", "asset_description", "asset_details",
                                      "asset_manufacturer", "asset_model", "asset_serial_number", "person_responsible",
                                      "person_responsible_email", "amrc_group_responsible__group_name", "requires_insurance",
                                      "requires_unforseen_damage_insurance", "asset_value", "charge_out_rate", "charge_code",
                                      "purchase_order_ref", "grn_id", "funded_by", "acquired_on", "disposal_date", "disposal_method",
                                      "dispatch_note_id", "requires_safety_checks", "safety_notes", "requires_environmental_checks",
                                      "environmental_aspects__aspect", "environmental_notes", "emergency_response_information",
                                      "requires_planned_maintenance", "maintenance_records", "maintenance_notes", "requires_calibration",
                                      "calibration_frequency", "passed_calibration", "calibration_date_prev", "calibration_date_next",
                                      "calibration_status__status_name", "calibration_type", "asset_location_building__building_name",
                                      "asset_location_room", "edited_by__username", "edited_on")
            return render_to_csv_response(output, filename="Custom_Filtered_Assets_{}.csv".format(str(timezone.now().date())))
        else:
            # User selected Website output on form
            number = len(filter.qs)
            if not number:
                number = "0"
            return render(request, "assetregister/asset_list_filtered.html", {"filter": filter, "number": number})
    else:
        # This is a bit hacky, but should work basically forever
        filter = AssetFilter(request.GET, queryset=Asset.objects.filter(asset_status="99999"))
        return render(request, "assetregister/asset_list_filtered.html", {"filter": filter})


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    assetcalibrations_3 = CalibrationRecord.objects.filter(asset=pk).order_by("-calibration_date", "-calibration_record_id")[:3]
    assetcalibrations_all = CalibrationRecord.objects.filter(asset=pk).order_by("-calibration_date", "-calibration_record_id")
    parent_of = Asset.objects.filter(parent_assets=pk)
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


@login_required
def asset_detail_equipid(request, equipid):
    asset = get_object_or_404(Asset, amrc_equipment_id=equipid)
    pk = asset.asset_id
    return asset_detail(request, pk)


@login_required
def asset_qr(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/asset_qr.html", {"asset": asset, "baseurl": baseurl})


@login_required
def asset_qr_small(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/asset_qr_small.html", {"asset": asset, "baseurl": baseurl})


@background()
def calibrated_asset_email(pk):
    asset = Asset.objects.get(pk=pk)
    CalEmails = CalibrationAssetNotificaton.objects.all().values_list("email_address", flat=True)
    email_subject = "[AMRC AssetMgt] Asset Requires Calibration"
    mail_body = """An asset on the AMRC Asset Management System has just been set to "Requires Calibration".
                 <br /><br /> "Asset No. {}" <br /><br />
                 <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System
                 """.format(asset, settings.BASEURL, asset.asset_id)
    logger.warning("[{}] - I've sent a '{}' email to {}".format(str(timezone.now()), email_subject, CalEmails))
    send_mail(email_subject, "", settings.EMAIL_FROM, CalEmails, fail_silently=False, html_message=mail_body)


@background()
def high_value_asset_email(pk):
    asset = Asset.objects.get(pk=pk)
    value = asset.asset_value
    allnotifications = HighValueAssetNotification.objects.all()
    email_subject = "[AMRC AssetMgt] High Value Asset"
    for notification in allnotifications:
        email_on_value = notification.if_asset_value_above
        if value >= email_on_value:
            email_to = HighValueAssetNotification.objects.filter(pk=notification.pk).values_list("email_address", flat=True)
            mail_body = """An asset on the AMRC Asset Management System has just had it's value set to be greater than your trigger value of £{}.
                     <br /><br /> "Asset No. {}" <br />
                     Asset Value = £{} <br /><br />
                     <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System,
                     or <a href="{}/staff/assetregister/highvalueassetnotification/">click here</a> to edit your notifcation trigger.
                     """.format(email_on_value, asset, value, settings.BASEURL, asset.asset_id, settings.BASEURL)
            logger.warning("[{}] - I've sent a '{}' email to {}".format(str(timezone.now()), email_subject, email_to))
            send_mail(email_subject, "", settings.EMAIL_FROM, email_to, fail_silently=False, html_message=mail_body)


@background()
def enviro_aspect_asset_email(pk):
    asset = Asset.objects.get(pk=pk)
    EnviroEmails = EnvironmentalAspectAssetNoficiation.objects.all().values_list("email_address", flat=True)
    aspectlist = ", ".join(ea.aspect for ea in asset.environmental_aspects.all())
    email_subject = "[AMRC AssetMgt] Asset With Environmental Aspects"
    mail_body = """An asset on the AMRC Asset Management System has just been associated with Environmental Aspects.<br /><br />
                 "Asset No. {}" <br /><br />
                 Environmental Aspects: {} <br /><br />
                 <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System
                 """.format(asset, aspectlist, settings.BASEURL, asset.asset_id)
    logger.warning("[{}] - I've sent a '{}' email to {}".format(str(timezone.now()), email_subject, EnviroEmails))
    send_mail(email_subject, "", settings.EMAIL_FROM, EnviroEmails, fail_silently=False, html_message=mail_body)


@background()
def asset_archived_email(pk, userid):
    user_making_change = User.objects.get(id=userid)
    user_email = user_making_change.email
    if user_email != "j.crease@amrc.co.uk" and user_email != "p.campsill@amrc.co.uk":
        user_name = user_making_change.get_full_name()
        asset = Asset.objects.get(pk=pk)
        email_to = ArchivedAssetNotificaton.objects.all().values_list("email_address", flat=True)
        email_subject = "[AMRC AssetMgt] Asset Status Set To Archived"
        mail_body = """An asset on the AMRC Asset Management System has just been set to "Archived" by {} ({}).
                     <br /><br /> "Asset No. {}" <br /><br />
                     <a href="{}/asset/{}">Click here</a> to view the asset on the AMRC Asset Management System
                     """.format(user_name, user_email, asset, settings.BASEURL, asset.asset_id)
        logger.warning("[{}] - I've sent a '{}' email to {}".format(str(timezone.now()), email_subject, email_to))
        print("[{}] - I've sent a '{}' email to {}""".format(str(timezone.now()), email_subject, email_to))
        send_mail(email_subject, "", settings.EMAIL_FROM, email_to, fail_silently=False, html_message=mail_body)


@login_required
@group_required("AddEditAssets", "AddEditCalibrations")
def calibration_asset_new(request):
    if request.method == "POST":
        form = NewAssetCalibrationInfo(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            asset.requires_insurance = False
            asset.requires_safety_checks = False
            asset.requires_environmental_checks = False
            asset.requires_planned_maintenance = False
            manual_qr_id = form.cleaned_data["asset_qr_location_manual"]
            if manual_qr_id:
                qrlocation = get_object_or_404(QRLocation, pk=manual_qr_id)
                asset.asset_qr_location = qrlocation
            asset.save()
            form.save_m2m()
            if asset.requires_calibration:
                calibrated_asset_email(asset.asset_id)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = NewAssetCalibrationInfo()
    return render(request, "assetregister/asset_edit.html", {"form": form})


@login_required
@group_required("AddEditAssets", "Finance", "AddEditCalibrations", "SuperUsers")
def asset_new(request):
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            manual_qr_id = form.cleaned_data["asset_qr_location_manual"]
            if manual_qr_id:
                qrlocation = get_object_or_404(QRLocation, pk=manual_qr_id)
                asset.asset_qr_location = qrlocation
            # manual_parents = form.cleaned_data["parent_manual"]
            # cleaned_parents = manual_parents.remove("")
            asset.save()
            form.save_m2m()
            if asset.requires_calibration:
                calibrated_asset_email(asset.asset_id)
            if asset.environmental_aspects.all().count() > 0:
                enviro_aspect_asset_email(asset.asset_id)
            if asset.asset_value:
                high_value_asset_email(asset.asset_id)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset()
        fields = list(form)
        topfields = fields[:16]
        safetyfields = fields[16:19]
        envirofields = fields[19:22]
        maintenancefields = fields[22:26]
        financefields = fields[26:35]
        everythingelse = fields[35:]
        breadcrumb = "New"
    return render(request, "assetregister/asset_edit_grouped.html", {"form": form, "topfields": topfields, "breadcrumb": breadcrumb,
                                                                     "safetyfields": safetyfields, "envirofields": envirofields,
                                                                     "maintenancefields": maintenancefields, "financefields": financefields,
                                                                     "everythingelse": everythingelse})


@login_required
@group_required("AddEditAssets", "Finance", "AddEditCalibrations", "SuperUsers")
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    assets_to_relate = Asset.objects.exclude(pk=pk).order_by("asset_manufacturer", "asset_description")
    cur_calibration_status = asset.requires_calibration
    cur_enviro_aspects = str(asset.environmental_aspects.all())  # this has to become a str now or will return the new values!
    cur_value = asset.asset_value
    cur_status = asset.asset_status
    current_qr_location = asset.asset_qr_location
    current_parent_assets = list(asset.parent_assets.all())
    if request.method == "POST":
        form = EditAsset(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.edited_by = request.user
            asset.edited_on = timezone.now()

            manual_qr_id = form.cleaned_data["asset_qr_location_manual"]
            qr_id = form.cleaned_data["asset_qr_location"]
            if current_qr_location == qr_id and manual_qr_id != qr_id:
                # manual_qr_id is different from cur so store manual value, otherwise let qr_id auto-save
                if not manual_qr_id:
                    asset.asset_qr_location = None
                else:
                    qrlocation = get_object_or_404(QRLocation, pk=manual_qr_id)
                    asset.asset_qr_location = qrlocation

            asset.save()

            parent_assets = form.cleaned_data["parent_assets"]
            parent_assets_manual = form.cleaned_data["parent_assets_manual"]
            parent_assets_manual = "".join(parent_assets_manual.split())    # remove all whitespace
            # swapping commas for whitespace allows split() to discount consecutive delimiters
            parent_assets_manual = parent_assets_manual.replace(",", " ")
            parent_assets_manual = set(parent_assets_manual.split())    # now make a deduped list
            parent_assets_manual_list = []
            for asset_id in parent_assets_manual:
                asset_to_relate = Asset.objects.get(pk=asset_id)
                parent_assets_manual_list.append(asset_to_relate)
            parent_assets_manual = parent_assets_manual_list

            if set(current_parent_assets) == set(parent_assets) and set(parent_assets_manual) != set(parent_assets):
                if not parent_assets_manual:
                    asset.parent_assets.clear()
                else:
                    asset.parent_assets.clear()
                    asset.parent_assets.add(*parent_assets_manual)
            else:
                form.save_m2m()

            if cur_calibration_status != asset.requires_calibration and asset.requires_calibration:
                # Calibration status has just changed and is now true
                calibrated_asset_email(asset.asset_id)

            if cur_enviro_aspects != str(asset.environmental_aspects.all()) and asset.environmental_aspects.all().count() > 0:
                # Enviro aspects have changed and asset has > 0 aspects
                enviro_aspect_asset_email(asset.asset_id)

            if cur_value != asset.asset_value and asset.asset_value:
                # Value has changed and asset has value
                high_value_asset_email(asset.asset_id)

            if cur_status != asset.asset_status and asset.asset_status:
                # Status has changed and asset has status
                new_status = asset.asset_status
                logger.warning("[{}] - User {} just changed asset status for asset ID {} ({}) from {} to {}".format(
                                                                                                                    timezone.now(),
                                                                                                                    request.user,
                                                                                                                    pk,
                                                                                                                    asset,
                                                                                                                    cur_status,
                                                                                                                    new_status
                                                                                                                    ))
                if new_status.id == 5:
                    # Status has changed to "achived" or equivalant
                    asset_archived_email(asset.asset_id, request.user.id)

            if current_qr_location != asset.asset_qr_location:
                logger.warning("[{}] - User {} just changed location for asset ID {} ({})".format(
                                                                                                  timezone.now(),
                                                                                                  request.user,
                                                                                                  pk,
                                                                                                  asset.asset_description
                                                                                                  ))
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAsset(instance=asset)

    if asset.asset_qr_location:
        form.fields["asset_qr_location_manual"].initial = asset.asset_qr_location.pk

    if asset.parent_assets.count() > 0:
        relatedids = []
        relatedassets = asset.parent_assets.all()
        for i in relatedassets:
            relatedids.append(i.pk)
        relatedstring = ", ".join([str(i) for i in relatedids])
        form.fields["parent_assets_manual"].initial = relatedstring

    fields = list(form)
    topfields = fields[:16]
    safetyfields = fields[16:19]
    envirofields = fields[19:22]
    maintenancefields = fields[22:26]
    financefields = fields[26:35]
    everythingelse = fields[35:]
    breadcrumb = "Edit"
    return render(request, "assetregister/asset_edit_grouped.html", {"form": form, "assets_to_relate": assets_to_relate, "topfields": topfields,
                                                                     "safetyfields": safetyfields, "envirofields": envirofields,
                                                                     "maintenancefields": maintenancefields, "financefields": financefields,
                                                                     "everythingelse": everythingelse, "breadcrumb": breadcrumb})


@login_required
@group_required("AddEditCalibrations")
def edit_asset_calibration_info(request, pk):
    type = "Calibration"
    asset = get_object_or_404(Asset, pk=pk)
    asset_id = asset.asset_id
    asset_description = asset.asset_description
    asset_manufacturer = asset.asset_manufacturer
    cur_calibration_status = asset.requires_calibration
    cur_status = asset.asset_status
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
            if cur_status != asset.asset_status and asset.asset_status:
                new_status = asset.asset_status
                logger.warning("[{}] - User {} just changed asset status for asset ID {} ({}) from {} to {}".format(
                    timezone.now(), request.user, pk, asset, cur_status, new_status))
                if new_status.id == 5:
                    # Status has changed to "achived" or equivalant
                    asset_archived_email(asset.asset_id, request.user.id)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAssetCalibrationInfo(instance=asset)
    return render(
                  request,
                  "assetregister/asset_edit_disabledfields.html",
                  {"form": form, "type": type,
                   "asset_id": asset_id, "manufacturer": asset_manufacturer,
                   "description": asset_description
                   })


@login_required
@group_required("Finance")
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
            if cur_value != asset.asset_value and asset.asset_value:
                # Value has changed and has value
                high_value_asset_email(asset.asset_id)
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAssetFinanceInfo(instance=asset)
    return render(
                  request,
                  "assetregister/asset_edit_disabledfields.html", {
                                                                   "form": form,
                                                                   "type": type,
                                                                   "asset_id": asset_id,
                                                                   "manufacturer": asset_manufacturer,
                                                                   "description": asset_description
                                                                   })


@login_required
@group_required("AddEditAssets", "SuperUsers", "AddEditCalibrations")
def reserve_assets(request):
    form_message = """This form will register the number of assets listed in "Number of Asset Records To Reserve"
         all containing identical information as listed in the fields below.  Reserved assets will have a status of
         "Archived" until changed."""
    form_title = "Bulk Reserve Assets"
    if request.method == "POST":
        form = ReserveAssets(request.POST)
        if form.is_valid():
            bulk_asset_description = form.cleaned_data["asset_description"]
            bulk_person_responsible = form.cleaned_data["person_responsible"]
            bulk_person_responsible_email = form.cleaned_data["person_responsible_email"]
            bulk_group_responsible = form.cleaned_data["amrc_group_responsible"]
            number_of_records_to_reserve = form.cleaned_data["number_of_records_to_reserve"]
            bulk_asset_edited_by = request.user

            logger.warning("[{}] - User {} just reserved {} assets records with description: {}".format(
                timezone.now(), bulk_asset_edited_by, number_of_records_to_reserve, bulk_asset_description))

            for i in range(number_of_records_to_reserve):
                Asset(asset_status_id="5", asset_description=bulk_asset_description, person_responsible=bulk_person_responsible,
                      person_responsible_email=bulk_person_responsible_email, amrc_group_responsible=bulk_group_responsible,
                      requires_insurance=False, requires_safety_checks=False, requires_environmental_checks=False,
                      requires_planned_maintenance=False, requires_calibration=False, edited_by=bulk_asset_edited_by).save()

            latest_asset = Asset.objects.order_by("-pk")[0]
            latest_asset_no = latest_asset.pk
            earliest_asset_no = (latest_asset_no - number_of_records_to_reserve) + 1
            success_message = "Reserved AMRC Asset IDs {} to {} (inclusive)".format(earliest_asset_no, latest_asset_no)
            print_labels = True
            return render(request, "assetregister/simple_message.html", {"message": success_message, "print_labels": print_labels,
                                                                         "earliest_asset_no": earliest_asset_no,
                                                                         "latest_asset_no": latest_asset_no})
    else:
        form = ReserveAssets()
    return render(request, "assetregister/asset_edit.html", {"form": form, "message": form_message, "title": form_title})


@login_required
@group_required("SuperUsers")
def print_asset_labels(request, id_from, id_to):

    if int(id_from) > int(id_to):
        message = "Oh No!  Something went wrong..."
        small_message = "ID_from ({}) was greater than ID_to ({})!".format(id_from, id_to)
        return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})

    if int(id_to) > 1000000:
        message = "Oh No!  Something went wrong..."
        small_message = """IDs over 1,000,000 won't print correctly with the current label design!
         You'll need to redesign the label's zpl code in Asset Management System Source Code views_locations.py and views_assets.py"""
        return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})

    try:
            import socket

            TCP_IP = "amrcf2050zebra1"
            TCP_PORT = 9100

            ids = range(int(id_from), int(id_to) + 1)
            for i in ids:

                length = len(str(i))
                if length <= 2:
                    id_width = 225
                    url_width = 524
                elif length == 3:
                    id_width = 250
                    url_width = 534
                elif length == 4:
                    id_width = 275
                    url_width = 544
                elif length == 5:
                    id_width = 300
                    url_width = 554
                elif length >= 6:
                    id_width = 325
                    url_width = 564

                zpl = """
                ^XA
                ^MMT
                ^PW600
                ^LL0300
                ^LS0
                ^FT353,310^BQN,2,8
                ^FH\^FDLA,https://amrcassets.shef.ac.uk/asset/{0}^FS
                ^FT343,229^A0I,62,60^FB324,1,0,C^FH\^FDAMRC ASSET^FS
                ^FT{1},92
                ^A0I,108,103
                ^FH\
                ^FD{0}^FS
                ^FT{2},23^A0I,30,30^FH\^FDhttps://amrcassets.shef.ac.uk/asset/{0}^FS
                ^PQ1,0,1,Y^XZ""".format(i, id_width, url_width)

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((TCP_IP, TCP_PORT))
                s.send(bytes(zpl, "utf-8"))
                s.close()

            message = "Success!"
            small_message = "Printed {} Asset Labels with IDs {} to {}".format(len(ids), id_from, id_to)
            return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})

    except Exception as e:
        message = "Oh No!  Something went wrong..."
        small_message = "{} - {}".format(e, type(e))
        return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})


@method_decorator(group_required("SuperUsers"), name="dispatch")
class asset_confirm_delete(DeleteView):
    model = Asset
    success_url = reverse_lazy("asset_list")


# @login_required
# class NewSearchView(SearchView):
#     template_name = 'search/search.html'
#     queryset = SearchQuerySet().exclude(asset_id=999999999999999999999999)
#     form_class = HighlightedSearchFormAssets
