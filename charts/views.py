from datetime import datetime
from django.http import JsonResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
import json

from smarthome_admin.models import TemperatureRecord, TemperatureZone


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        #elif isinstance(obj, datetime.date):
        #    return obj.strftime('%Y-%m-%d')
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def temperature_chart_view(request, num):
    try:
        zone = TemperatureZone.objects.get(pk=num)
        records = list(TemperatureRecord.objects.filter(zone=zone)[:3000].values_list("time", "temperature"))
    except TemperatureZone.DoesNotExist:
        raise Http404

    return JsonResponse(records, safe=False, encoder=DatetimeEncoder)



def temperature_chart_zones(request):
    zones = TemperatureZone.objects.all()

    return render_to_response("graph.html", {"zones": zones}, context_instance=RequestContext(request))

