from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from assetregister.models import Asset, CalibrationRecord
from assetregister.decorators import group_required
from djqscsv import render_to_csv_response
from django.http import HttpResponseNotFound


@login_required
def calibrated_asset_export_active(request):
    calibration_export = Asset.objects.filter(requires_calibration=True,
                                              asset_status=1).order_by("calibration_date_next").values(
                                                "asset_id", "amrc_equipment_id", "requires_calibration", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "calibration_date_prev", "calibration_date_next",
                                                "calibration_procedure", "person_responsible",
                                                "person_responsible_email", "asset_location_building__building_name",
                                                "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Active_Assets_Needing_Calibration_{}.csv".format(str(timezone.now().date())))


@login_required
def calibrated_asset_export_all(request):
    calibration_export = Asset.objects.filter(requires_calibration=True).order_by("calibration_date_next").values(
                                                "asset_id", "amrc_equipment_id", "requires_calibration", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "calibration_date_prev", "calibration_date_next",
                                                "calibration_procedure", "person_responsible",
                                                "person_responsible_email", "asset_location_building__building_name",
                                                "asset_location_room")
    return render_to_csv_response(calibration_export, filename="All_Assets_Needing_Calibration_{}.csv".format(str(timezone.now().date())))


@login_required
@group_required('AddEditCalibrations', 'SuperUsers')
def calibration_asset_export_nextmonth(request):
    plusonemonth = timezone.now() + timedelta(days=30)
    calibration_export = Asset.objects.filter(
            requires_calibration=True, calibration_date_next__lte=plusonemonth).order_by("calibration_date_next").values(
            "asset_id", "amrc_equipment_id", "requires_calibration", "asset_description", "asset_manufacturer",
            "asset_model", "asset_serial_number", "asset_status__status_name", "calibration_date_prev",
            "calibration_date_next", "calibration_procedure", "person_responsible", "person_responsible_email",
            "asset_location_building__building_name", "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Assets_Due_Calibration_Before_{}.csv".format(str(plusonemonth.date())))


@login_required
@group_required('AddEditCalibrations', 'SuperUsers')
def calibration_asset_export_custom_select(request):
    return render(request, "assetregister/calibration_export.html")


@login_required
@group_required('AddEditCalibrations', 'SuperUsers')
def calibration_asset_export_custom(request):
    if request.GET.get('days'):
        getdays = int(request.GET.get('days'))
        newdate = timezone.now() + timedelta(days=getdays)
        newdate = newdate.date()
    elif request.GET.get('date'):
        newdate = request.GET.get('date')
    else:
        return HttpResponseNotFound('<h2>No "days" or "date" selected!</h2>')
    calibration_export = Asset.objects.filter(requires_calibration=True, calibration_date_next__lte=newdate).order_by(
                                "calibration_date_next"
                                ).values(
                                         "asset_id", "requires_calibration", "asset_description", "asset_manufacturer",
                                         "asset_model", "asset_serial_number", "asset_status__status_name",
                                         "calibration_date_prev", "calibration_date_next", "calibration_procedure",
                                         "person_responsible", "person_responsible_email",
                                         "asset_location_building__building_name", "asset_location_room")
    return render_to_csv_response(calibration_export, filename="Assets_Due_Calibration_Before_{}.csv".format(str(newdate)))


@login_required
def maintenance_export_all(request):
    export = Asset.objects.filter(requires_planned_maintenance=True).order_by("asset_id").values(
                                                "asset_id", "requires_planned_maintenance", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "person_responsible", "person_responsible_email",
                                                "maintenance_instructions", "maintenance_records",
                                                "asset_location_building__building_name",
                                                "asset_location_building__EFM_building_code",
                                                "asset_location_room", "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Maintenance_{}.csv".format(str(timezone.now().date())))


@login_required
def environmental_export_all(request):
    export = Asset.objects.filter(requires_environmental_checks=True).order_by("asset_id").values(
                                                "asset_id", "requires_environmental_checks", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "person_responsible", "person_responsible_email",
                                                "asset_location_building__building_name",
                                                "asset_location_building__EFM_building_code",
                                                "asset_location_room", "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Environmental_Checks_{}.csv".format(str(timezone.now().date())))


@login_required
def insurance_export_all(request):
    export = Asset.objects.filter(requires_insurance=True).order_by("asset_id").values(
                                                "asset_id", "requires_insurance", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "asset_value", "purchase_order_ref",
                                                "funded_by", "acquired_on", "person_responsible", "person_responsible_email",
                                                "asset_location_building__building_name",
                                                "asset_location_building__EFM_building_code",
                                                "asset_location_room", "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Insurance_{}.csv".format(str(timezone.now().date())))


@login_required
def safety_export_all(request):
    export = Asset.objects.filter(requires_safety_checks=True).order_by("asset_id").values(
                                                "asset_id", "requires_safety_checks", "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "person_responsible", "person_responsible_email",
                                                "asset_location_building__building_name",
                                                "asset_location_building__EFM_building_code",
                                                "asset_location_room", "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Assets_Needing_Safety_Checks_{}.csv".format(str(timezone.now().date())))


@login_required
def location_export_all(request):
    export = Asset.objects.all().order_by("asset_location_building__building_name").values(
                                                "asset_location_building__building_name",
                                                "asset_location_building__EFM_building_code",
                                                "asset_location_room",
                                                "asset_id", "requires_safety_checks", "requires_insurance",
                                                "requires_environmental_checks", "requires_planned_maintenance",
                                                "asset_description",
                                                "asset_manufacturer", "asset_model", "asset_serial_number",
                                                "asset_status__status_name", "person_responsible", "person_responsible_email",
                                                "handling_and_storage_instructions")
    return render_to_csv_response(export, filename="All_Asset_Records_By_Location_{}.csv".format(str(timezone.now().date())))


@login_required
@group_required('SuperUsers')
def export_all_assets(request):
    export = Asset.objects.all()
    return render_to_csv_response(export, filename="All_Assets__{}.csv".format(str(timezone.now().date())))


@login_required
@group_required('AddEditCalibrations', 'SuperUsers')
def export_all_calibratons(request):
    export = CalibrationRecord.objects.order_by("-calibration_date").values(
                                                "calibration_record_id", "asset", "asset__asset_description",
                                                "asset__asset_manufacturer", "calibration_description",
                                                "calibration_date", "calibration_date_next", "calibrated_by_internal__username",
                                                "calibrated_by_external", "calibration_outcome", "calibration_notes",
                                                "calibration_certificate", "calibration_entered_by__username", "calibration_entered_on")
    return render_to_csv_response(export, filename="All_Calibration_Records_{}.csv".format(str(timezone.now().date())))
