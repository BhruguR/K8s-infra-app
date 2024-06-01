from django.shortcuts import render

from django.template import Context, loader


def index (request):
    template = loader.get_template("quotes/route2.html")
    return render(request, 'quotes/route2.html')
