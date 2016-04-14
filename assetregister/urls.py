from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.asset_list, name="asset_list")
]