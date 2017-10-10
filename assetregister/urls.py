from django.conf.urls import include, url
from . import views
#from assetregister.views import NewSearchView
from django.conf import settings

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^calibration/$', views.calibration_list, name="calibration_list"),
    url(r'^calibration/new/$', views.new_calibration, name="new_calibration"),
    url(r'^calibration/new/(?P<urlpk>\d+)/$', views.new_calibration_asset, name="new_calibration_asset"),
    url(r'^calibration/assets/$', views.calibrated_asset_list, name="calibrated_asset_list"),
    url(r'^calibration/assets/active$', views.calibrated_asset_list_active, name="calibrated_asset_list_active"),
    url(r'^calibration/export/active/$', views.calibrated_asset_export_active, name="calibrated_asset_export_active"),
    url(r'^calibration/export/all/$', views.calibrated_asset_export_all, name="calibrated_asset_export_all"),
    url(r'^calibration/export/all/nextmonth/$', views.calibration_asset_export_nextmonth,
        name="calibration_asset_export_nextmonth"),
    url(r'^calibration/export/custom/$', views.calibration_asset_export_custom, name="calibration_asset_export_custom"),
    url(r'^calibration/export/$', views.calibration_asset_export_custom_select,
        name="calibration_asset_export_custom_select"),
    url(r'^calibration/export/records/$', views.export_all_calibratons, name="export_calibration_records"),
    url(r'^calibration/(?P<slug>[-\w]+)/$', views.calibration_detail, name="calibration_detail"),
    url(r'^calibration/(?P<slug>[-\w]+)/edit$', views.calibration_edit, name="calibration_edit"),
    url(r'^calibration/(?P<slug>[-\w]+)/remove/$', views.calibration_confirm_delete.as_view(), name="calibration_confirm_delete"),
    url(r'^asset/$', views.asset_list, name="asset_list"),
    url(r'^asset/active/$', views.active_asset_list, name="active_asset_list"),
    url(r'^asset/new/$', views.asset_new, name="asset_new"),
    url(r'^asset/new/calibration$', views.calibration_asset_new, name="calibration_asset_new"),
    url(r'^asset/bulk_reserve/$', views.reserve_assets, name="reserve_assets"),
    url(r'^asset/(?P<pk>\d+)/edit/calibration/$', views.edit_asset_calibration_info, name="edit_asset_calibration_info"),
    url(r'^asset/(?P<pk>\d+)/edit/finance/$', views.edit_asset_finance_info, name="edit_asset_finance_info"),
    url(r'^asset/(?P<pk>\d+)/edit/location/$', views.edit_asset_location, name="edit_asset_location"),
    url(r'^asset/(?P<pk>\d+)/edit/$', views.asset_edit, name="asset_edit"),
    url(r'^asset/(?P<pk>\d+)/remove/$', views.asset_confirm_delete.as_view(), name="asset_confirm_delete"),
    url(r'^asset/(?P<pk>\d+)/qr/small/$', views.asset_qr_small, name="asset_qr_small"),
    url(r'^asset/(?P<pk>\d+)/qr/$', views.asset_qr, name="asset_qr"),
    url(r'^asset/(?P<pk>\d+)/$', views.asset_detail, name="asset_detail"),
    url(r'^asset/equip-id/(?P<equipid>[-\w]+)/$', views.asset_detail_equipid, name="asset_detail_equipid"),
    url(r'^search/', include("haystack.urls")),
    url(r'^search/advanced/$', views.asset_list_filter, name="asset_list_filter"),
    url(r'^asset/export/all/$', views.export_all_assets, name="asset_export_all"),
    url(r'^maintenance/export/all/$', views.maintenance_export_all, name="maintenance_export_all"),
    url(r'^environmental/export/all/$', views.environmental_export_all, name="environmental_export_all"),
    url(r'^insurance/export/all/$', views.insurance_export_all, name="insurance_export_all"),
    url(r'^safety/export/all/$', views.safety_export_all, name="safety_export_all"),
    url(r'^location/export/all/$', views.location_export_all, name="location_export_all"),
    #url(r'^newsearch/?$', NewSearchView.as_view(), name='new_search_view'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
