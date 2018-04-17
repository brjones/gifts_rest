from restui.models.ensembl import EnsemblGene
from restui.serializers.ensembl import EnsemblGeneSerializer

from django.shortcuts import render
from rest_framework import mixins
from rest_framework import generics
import pprint

class EnsemblFeature(mixins.CreateModelMixin,
                     generics.GenericAPIView):

    serializer_class = EnsemblGeneSerializer

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]

        if isinstance(data, list):
            kwargs["many"] = True

            return super(EnsemblFeature, self).get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        objs = self.create(request, *args, **kwargs)
        pprint.pprint(objs)
        return objs
    
    def get(self, request, *args, **kwargs):
        print("Got here")
        