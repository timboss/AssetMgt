from django.shortcuts import render

# Create your views here.

def asset_list(request):
    return render(request, "assetregister/asset_list.html", {})