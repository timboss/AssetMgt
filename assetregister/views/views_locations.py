from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from assetregister.models import (
                                  Asset,
                                  QRLocation
                                  )
from assetregister.forms import (
                                 EditAssetLocationInfo,
                                 NewQRLocation,
                                 EditQRLocation,
                                 ReserveLocations,
                                 MoveAssetToQRLocation,
                                 QRLocationFilter
                                 )
from assetregister.decorators import group_required
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
def qr_location_qr(request, pk):
    location = get_object_or_404(QRLocation, pk=pk)
    baseurl = settings.BASEURL
    return render(request, "assetregister/location_qr_small.html", {"location": location, "baseurl": baseurl})


@login_required
def new_qr_location(request):
    if request.method == "POST":
        form = NewQRLocation(request.POST)
        if form.is_valid():
            qrlocation = form.save()
            success_message = "Added New AMRC Asset QR Location I.D. {}.".format(qrlocation.pk)
            small_message = """Redirect to location page - list of assets at location and button to print location qr"""
            return render(request, "assetregister/simple_message.html", {"message": success_message, "smallmessage": small_message})
    else:
        form = NewQRLocation()
    form_title = "Create New Asset QR Location"
    qrlocation = "QR Locations"
    return render(request, "assetregister/asset_edit.html", {"form": form, "title": form_title, "qrlocation": qrlocation})


@login_required
def edit_qr_location(request, pk):
    location = get_object_or_404(QRLocation, pk=pk)
    if request.method == "POST":
        form = EditQRLocation(request.POST, instance=location)
        if form.is_valid():
            qrlocation = form.save()
            success_message = "Added New AMRC Asset QR Location I.D. {}.".format(qrlocation.pk)
            small_message = """Redirect to location page - list of assets at location and button to print location qr"""
            return render(request, "assetregister/simple_message.html", {"message": success_message, "smallmessage": small_message})
    else:
        form = EditQRLocation(instance=location)
    form_title = "Edit an Asset QR Location"
    qrlocation = "QR Location {}".format(pk)
    return render(request, "assetregister/edit_location_disabledfields.html", {"form": form, "title": form_title, "location_id": pk,
                                                                               "qrlocation": qrlocation
                                                                               })


@login_required
@group_required("SuperUsers", "AddEditAssets")
def reserve_qr_locations(request):
    form_message = """This form will register the number of asset locations listed in "Number of Asset QR Locations Records To Reserve"
         all containing identical information as listed in the fields below."""
    form_title = "Bulk Reserve QR Locations"
    if request.method == "POST":
        form = ReserveLocations(request.POST)
        if form.is_valid():
            bulk_location_building = form.cleaned_data["location_building"]
            bulk_location_room = form.cleaned_data["location_room"]
            number_of_records_to_reserve = form.cleaned_data["number_of_records_to_reserve"]
            reserved_by = request.user

            logger.warning("[{}] - User {} just reserved {} QR Location records with building={} and room={}".format(
                timezone.now(), reserved_by, number_of_records_to_reserve, bulk_location_building, bulk_location_room))

            for i in range(number_of_records_to_reserve):
                QRLocation(building=bulk_location_building, location_room=bulk_location_room).save()

            latest_location = QRLocation.objects.filter(building=bulk_location_building, location_room=bulk_location_room).order_by("-pk")[0]
            latest_location_id = latest_location.pk
            earliest_location_id = (latest_location_id - number_of_records_to_reserve) + 1
            success_message = "Reserved AMRC Asset QR Location IDs {} to {} (inclusive)".format(earliest_location_id, latest_location_id)
            return render(request, "assetregister/simple_message.html", {"message": success_message})
    else:
        form = ReserveLocations()
    return render(request, "assetregister/asset_edit.html", {"form": form, "message": form_message, "title": form_title})


@login_required
def edit_asset_location(request, pk):
    type = "Location"
    message = """Setting an Asset QR Location will overwrite anything in the Asset Location Building or Specific
     Location or Room text fields with the Asset QR Location details"""
    asset = get_object_or_404(Asset, pk=pk)
    asset_id = asset.asset_id
    asset_description = asset.asset_description
    asset_manufacturer = asset.asset_manufacturer
    current_qr_location = asset.asset_qr_location
    if request.method == "POST":
        form = EditAssetLocationInfo(request.POST, instance=asset)
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
            logger.warning("[{}] - User {} just changed location for asset ID {} ({})".format(
                timezone.now(), request.user, pk, asset_description))
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = EditAssetLocationInfo(instance=asset)
    if asset.asset_qr_location:
        form.fields["asset_qr_location_manual"].initial = asset.asset_qr_location.pk
    return render(
                  request,
                  "assetregister/asset_edit_location.html", {
                                                             "form": form,
                                                             "message": message,
                                                             "type": type,
                                                             "asset": asset,
                                                             "asset_id": asset_id,
                                                             "manufacturer": asset_manufacturer,
                                                             "description": asset_description
                                                             })


@login_required
def move_asset_to_qr_location(request, pk):
    qrlocation = get_object_or_404(QRLocation, pk=pk)
    if request.method == "POST":
        form = MoveAssetToQRLocation(request.POST)
        if form.is_valid():
            asset_id = form.cleaned_data["asset_id"]
            asset = get_object_or_404(Asset, pk=asset_id)
            asset.asset_qr_location = qrlocation
            asset.edited_by = request.user
            asset.edited_on = timezone.now()
            logger.warning("[{}] - User {} just changed location for asset ID {} ({})".format(
                timezone.now(), request.user, asset_id, asset.asset_description))
            asset.save()
            return redirect("asset_detail", pk=asset_id)
    else:
        form = MoveAssetToQRLocation()
        assets_here_count = Asset.objects.filter(asset_qr_location=pk).count()
    return render(request, "assetregister/move_asset_to_qr_location.html", {"form": form, "qrlocation": qrlocation,
                                                                            "assetcount": assets_here_count})


@login_required
def qr_location_list(request):
    if request.GET:
        filter = QRLocationFilter(request.GET, queryset=QRLocation.objects.all())
        makecsv = request.GET.get("makecsv")
        if makecsv == "1":
            # User selected CSV output
            output = filter.qs.values("location_id", "building__building_name", "building__EFM_building_code", "location_room")
            return render_to_csv_response(output, filename="Custom_Filtered_QR_Locations_{}.csv".format(str(timezone.now().date())))
        else:
            # User selected Website output
            number = len(filter.qs)
            if not number:
                number = "0"
            #    paginator = Paginator(filter.qs, 20)
            #    page = request.GET.get('page')
            #    try:
            #        filter = paginator.page(page)
            #    except PageNotAnInteger:
            #        # If page is not an integer, deliver first page.
            #        filter = paginator.page(1)
            #    except EmptyPage:
            #        # If page is out of range (e.g. 9999), deliver last page of results.
            #        filter = paginator.page(paginator.num_pages)
            return render(request, "assetregister/location_qr_list_filtered.html", {"filter": filter, "number": number})
    else:
        # This is a bit hacky, but should work basically forever
        filter = QRLocationFilter(request.GET, queryset=QRLocation.objects.all())
        return render(request, "assetregister/location_qr_list_filtered.html", {"filter": filter})


@login_required
def qr_location_view_assets(request, pk):
    response = redirect("asset_list_filter")
    response["Location"] += "?asset_qr_location={}".format(pk)
    return response


@login_required
@group_required("SuperUsers")
def print_location_labels(request, id_from, id_to):

    if int(id_from) > int(id_to):
        message = "Oh No!  Something went wrong..."
        small_message = "ID_from ({}) was greater than ID_to ({})!".format(id_from, id_to)
        return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})

    if int(id_to) > 1000000:
        message = "Oh No!  Something went wrong..."
        small_message = """IDs over 1,000,000 won't print correctly with the current label design!
         You'll need to redesign the label's ZPL code in Asset Management System Source Code views_locations.py and views_assets.py"""
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
                    qr_top = 310
                    url_width = 544
                elif length == 3:
                    id_width = 250
                    qr_top = 310
                    url_width = 554
                elif length == 4:
                    id_width = 275
                    qr_top = 320
                    url_width = 564
                elif length == 5:
                    id_width = 300
                    qr_top = 320
                    url_width = 574
                elif length >= 6:
                    id_width = 325
                    qr_top = 320
                    url_width = 584

                zpl = """
                ^XA
                ^MMT
                ^PW600
                ^LL0300
                ^LS0
                ^FT353,{2}^BQN,2,8
                ^FH\^FDLA,https://amrcassets.shef.ac.uk/location/{0}^FS
                ^FT345,239^A0I,62,60^FB324,1,0,C^FH\^FDAMRC ASSET^FS
                ^FT345,179^A0I,62,60^FB324,1,0,C^FH\^FDLOCATION ID^FS
                ^FT{1},72
                ^A0I,108,103
                ^FH\
                ^FD{0}^FS
                ^FT{3},23^A0I,30,30^FH\^FDhttps://amrcassets.shef.ac.uk/location/{0}^FS
                ^PQ1,0,1,Y^XZ""".format(i, id_width, qr_top, url_width)

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((TCP_IP, TCP_PORT))
                s.send(bytes(zpl, "utf-8"))
                s.close()

            message = "Success!"
            small_message = "Printed {} QR Location Labels with IDs {} to {}".format(len(ids), id_from, id_to)
            return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})

    except Exception as e:
        message = "Oh No!  Something went wrong..."
        small_message = "{} - {}".format(e, type(e))
        return render(request, "assetregister/simple_message.html", {"message": message, "smallmessage": small_message})
