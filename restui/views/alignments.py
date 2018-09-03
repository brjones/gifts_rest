import pprint

from restui.models.mappings import Alignment, AlignmentRun
from restui.serializers.alignments import AlignmentSerializer, AlignmentRunSerializer

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

class AlignmentRunCreate(generics.CreateAPIView):
    """
    Store an AlignmentRun 
    """

    serializer_class = AlignmentRunSerializer

class AlignmentRunFetch(generics.RetrieveAPIView):
    """
    Retrieve an AlignmentRun
    """

    queryset = AlignmentRun.objects.all()
    serializer_class = AlignmentRunSerializer
    
class AlignmentCreate(generics.CreateAPIView):
    """
    Insert an Alignment
    """

    serializer_class = AlignmentSerializer

class AlignmentFetch(generics.RetrieveAPIView):
    """
    Retrieve an Alignment
    """

    queryset = Alignment.objects.all()
    serializer_class = AlignmentSerializer

