from django.conf.urls import include, url
from . import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.asset_list, name="asset_list"),
    url(r'^active/$', views.active_asset_list, name="active_asset_list"),
    url(r'^calibration/$', views.calibrated_asset_list, name="calibrated_asset_list"),
    url(r'^asset/(?P<pk>\d+)/$', views.asset_detail, name="asset_detail"),
    url(r'^asset/new/$', views.asset_new, name="asset_new"),
    url(r'^asset/(?P<pk>\d+)/edit/$', views.asset_edit, name="asset_edit"),
    url(r'^asset/(?P<pk>\d+)/remove/$', views.asset_confirm_delete.as_view(), name="asset_confirm_delete"),
    url(r'^asset/(?P<pk>\d+)/qr/small/$', views.asset_qr_small, name="asset_qr_small"),
    url(r'^asset/(?P<pk>\d+)/qr/$', views.asset_qr, name="asset_qr"),
    url(r'^search/calibration/', views.calibration_search.as_view(), name="calibration_search"),
    url(r'^search/', include("haystack.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]