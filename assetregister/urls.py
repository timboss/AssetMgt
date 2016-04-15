from django.conf.urls import url
from . import views
from django.conf import settings


urlpatterns = [
    url(r'^$', views.asset_list, name="asset_list"),
    url(r'^asset/(?P<pk>\d+)/$', views.asset_detail, name="asset_detail"),
]

