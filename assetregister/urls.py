from django.conf.urls import include, url
from . import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.asset_list, name="asset_list"),
    url(r'^active/$', views.active_asset_list, name="active_asset_list"),
    url(r'^calibration/$', views.calibration_list, name="calibration_list"),
    url(r'^calibration/(?P<pk>\d+)/$', views.calibration_detail, name="calibration_detail"),
    url(r'^calibration/(?P<pk>\d+)/edit$', views.calibration_edit, name="calibration_edit"),
    url(r'^calibration/(?P<pk>\d+)/remove/$', views.calibration_confirm_delete.as_view(), name="calibration_confirm_delete"),
    url(r'^calibration/assets/$', views.calibrated_asset_list, name="calibrated_asset_list"),
    url(r'^calibration/assets/active$', views.calibrated_asset_list_active, name="calibrated_asset_list_active"),
    url(r'^calibration/new/$', views.new_calibration, name="new_calibration"),
    url(r'^calibration/new/(?P<urlpk>\d+)/$', views.new_calibration_asset, name="new_calibration_asset"),
    url(r'^calibration/export/active/$', views.calibrated_asset_export_active, name="calibrated_asset_export_active"),
    url(r'^calibration/export/all/$', views.calibrated_asset_export_all, name="calibrated_asset_export_all"),
    url(r'^calibration/export/all/nextmonth/$', views.calibration_asset_export_nextmonth,
        name="calibration_asset_export_nextmonth"),
    url(r'^calibration/export/custom/$', views.calibration_asset_export_custom, name="calibration_asset_export_custom"),
    url(r'^calibration/export/$', views.calibration_asset_export_custom_select,
        name="calibration_asset_export_custom_select"),
    url(r'^asset/(?P<pk>\d+)/$', views.asset_detail, name="asset_detail"),
    url(r'^asset/new/$', views.asset_new, name="asset_new"),
    url(r'^asset/(?P<pk>\d+)/edit/$', views.asset_edit, name="asset_edit"),
    url(r'^asset/(?P<pk>\d+)/remove/$', views.asset_confirm_delete.as_view(), name="asset_confirm_delete"),
    url(r'^asset/(?P<pk>\d+)/qr/small/$', views.asset_qr_small, name="asset_qr_small"),
    url(r'^asset/(?P<pk>\d+)/qr/$', views.asset_qr, name="asset_qr"),
    url(r'^search/calibration/', views.calibration_search.as_view(), name="calibration_search"),
    url(r'^search/', include("haystack.urls")),
    url(r'^asset/export/all/$', views.export_all_assets, name="asset_export_all"),
    url(r'^maintenance/export/all/$', views.maintenance_export_all, name="maintenance_export_all"),
    url(r'^environmental/export/all/$', views.environmental_export_all, name="environmental_export_all"),
    url(r'^insurance/export/all/$', views.insurance_export_all, name="insurance_export_all"),
    url(r'^safety/export/all/$', views.safety_export_all, name="safety_export_all"),
    url(r'^example/$', views.example, name="example")
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
