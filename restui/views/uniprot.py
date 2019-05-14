"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from restui.models.uniprot import UniprotEntry
from restui.serializers.uniprot import UniprotEntrySerializer

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView


class UniprotEntryFetch(generics.RetrieveAPIView):
    """
    Retrieve a Uniprot entry by db ID
    """

    queryset = UniprotEntry.objects.all()
    serializer_class = UniprotEntrySerializer
