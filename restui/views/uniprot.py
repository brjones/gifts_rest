from restui.models.uniprot import UniprotEntry
from restui.serializers.uniprot import UniprotEntrySerializer

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

import pprint

class UniprotEntryFetch(generics.RetrieveAPIView):
    """
    Retrieve a Uniprot entry by db ID
    """

    queryset = UniprotEntry.objects.all()
    serializer_class = UniprotEntrySerializer

