from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers import ControllerPingSerializer
from rest_framework import status
__author__ = 'dmarkey'

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class ControllerPingCreate(APIView):
    def post(self, request, format=None):
        request.data['ip'] = get_client_ip(request)
        serializer = ControllerPingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)