from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from restui.serializers.service import StatusSerializer

class PingService(APIView):
    """
    Return service status (0 if ok)
    """
    
    def get(self, request):
        serializer = StatusSerializer( { 'ping': 0 } )
        return Response(serializer.data)

