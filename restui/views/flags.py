from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from restui.serializers.flags import EnsemblFlagSerializer, UniprotFlagSerializer


class EnsemblFlagStatus(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, version, format=None):
        """
        Return current flags status to check if action are authorized
        """
        serializer = EnsemblFlagSerializer(version)
        return Response(serializer.data)


class UniprotFlagStatus(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, version, format=None):
        """
        Return current flags status to check if action are authorized
        """
        serializer = UniprotFlagSerializer(version)
        return Response(serializer.data)
