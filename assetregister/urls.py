from django.conf.urls import include, url
from . import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.asset_list, name="asset_list"),
    url(r'^active/$', views.active_asset_list, name="active_asset_list"),
    url(r'^calibration/$', views.calibrated_asset_list, name="calibrated_asset_list"),
    url(r'^asset/(?P<pk>\d+)/$', views.asset_detail, name="asset_detail"),
    url(r'^asset/new/$', views.asset_new, name="asset_new"),
    url(r'^asset/(?P<pk>\d+)/edit/$', views.asset_edit, name='asset_edit'),
    url(r'^search/', include('haystack.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]