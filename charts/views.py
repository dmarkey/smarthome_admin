from chartit import DataPool, Chart
from django.shortcuts import render_to_response
from django.template import RequestContext

from smarthome_admin.models import TemperatureRecord, TemperatureZone


def temperature_chart_view(request, num):
    zone = TemperatureZone.objects.get(pk=num)
    # Step 1: Create a DataPool with the data we want to retrieve.
    temperaturedata = DataPool(
            series=
            [{'options': {
                'source': TemperatureRecord.objects.filter(zone__pk=num)},
                'terms': [
                    'time',
                    'temperature']}
            ])

    cht = Chart(
            datasource=temperaturedata,
            series_options=
            [{'options': {
                'type': 'line',
                'stacking': True},
                'terms': {
                    'time': [
                        'temperature']
                }}],
            chart_options=
            {'title': {
                'text': str(zone)},
                'xAxis': {
                    'type': 'datetime',
                    'title': {
                        'text': 'Time'}}})

    # Step 3: Send the chart object to the template.
    return render_to_response("graph.html", {'temperaturechart': cht}, context_instance=RequestContext(request))
