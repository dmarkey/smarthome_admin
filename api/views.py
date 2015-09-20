from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import routers
from .serializers import ControllerPingSerializer, SocketSerializer
from rest_framework import status
from smarthome_admin.models import Socket

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

router = routers.DefaultRouter()


class SocketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Socket.objects.all()
    serializer_class = SocketSerializer

    @method_decorator(ensure_csrf_cookie)
    def list(self, request, *args, **kwargs):
        return super(SocketViewSet, self).list(request, *args, **kwargs)

router.register(r'sockets', SocketViewSet)
